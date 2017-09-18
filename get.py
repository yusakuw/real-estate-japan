import sys
if sys.version_info.major != 3 or sys.version_info.minor < 6:
    raise RuntimeError('Python >= 3.6')

import urllib.request
import re
import time
import unicodedata
from bs4 import BeautifulSoup
from pymongo import MongoClient
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def main(argv):
    if len(argv) != 2:
        print('Usage: python get.py "http://www.fudousan.or.jp/system/?act=l&type=31&pref=13&stype=e&line%5B%5D=2184&eki%5B%5D=2184131&rl=l&rh=h&asl=l&ash=h&submitbtn=l"')
        return 1

    list_uri = argv[1].strip('\'"')
    if re.search('[?&]n=[0-9]+', list_uri) is None:
        list_uri += '&n=100'
    if re.search('[?&]p=[0-9]+', list_uri) is None:
        list_uri += '&p=1'

    # Database settings
    db = MongoClient(port=27017).realestate

    list_scraper = ListScraper()
    list_scraper.get_and_store_list(list_uri, db)
    return 0

class ListScraper:
    def __init__(self):
        self.results_limit = 1000
        self._scraper = Scraper()
        self._results_count = 0

    def get_and_store_list(self, list_uri, db):
        page_uri = list_uri
        while self._get_and_store_list_internal(page_uri, db):
            next_page = int(re.search(r'(?<=[?&]p=)[0-9]+', page_uri).group()) + 1
            page_uri = re.sub(r'(?<=[?&]p=)[0-9]+', str(next_page), page_uri)
            logger.debug('Get list page #' + str(next_page))

    def _get_and_store_list_internal(self, page_uri, db):
        html = urllib.request.urlopen(page_uri).read().decode('euc_jisx0213')
        soup = BeautifulSoup(html, 'html.parser')

        # 物件見出し == th.text_midashi
        th_results = soup.find_all(class_='text_midashi')
        if len(th_results) == 0:
            logger.debug('Finished.')
            return False
        if self._results_count == 0:
            self._results_count = int(re.search(r'[0-9]+(?=件中)', str(soup.select('.result_no p')[0])).group())
            logger.debug(f'Find {self._results_count} results')
        if self._results_count > self.results_limit:
            raise ValueError(f'Too many results (> {self.results_limit}). Try another URI.')

        for th in th_results:
            url = 'http://www.fudousan.or.jp/system/' + th.h5.a['href'].lstrip('./')
            title = next(th.h5.a.stripped_strings, None)
            logger.debug('Processing: ' + url)
            info = self._scraper.get_info(url, title)
            db.properties.replace_one({'ID':info['ID']}, info, upsert=True)
        return True

class Scraper:
    def __init__(self):
        self.scraping_interval = 3

    def get_info(self, url, title):
        info = {'ID': re.search(r'(?<=[\?&]bid=)[0-9]+', url).group(), 'URL': url}
        if title != '詳細情報はこちらです':
            info['物件名称'] = title

        time.sleep(self.scraping_interval)
        html = urllib.request.urlopen(url).read().decode('euc_jisx0213')
        soup = BeautifulSoup(html, 'html.parser')

        info['画像'] = [img.get('src') for img in soup.select('#photo_container img')]

        rent_raw = next(soup.find(class_='syousai_price').stripped_strings, None)
        if rent_raw is not None:
            info['家賃'] = self._convert_yenstr_to_int(rent_raw)
        else:
            raise ValueError(f'Cannot get rent value: "{rent_raw}"')

        info.update(self._parse_table(soup.find(id='info-table-1')))
        info.update(self._parse_table(soup.find(id='info-table-2')))
        info.update(self._parse_table(soup.find(id='info-table-5')))

        return self._modify_info(info)

    def _parse_table(self, table):
        dict = {}
        for th in table.find_all('th'):
            buff = []
            ptr = th
            while ptr.next_sibling.findNext().name == 'td':
                ptr = ptr.next_sibling.findNext()
                for img in ptr.find_all('img'):
                    buff.append(img['src'])
                for a in ptr.find_all('a'):
                    buff.append(a['href'])
                for txt in ptr.stripped_strings:
                    buff.append(txt)
            if len(buff) == 1:
                dict[th.string] = buff[0]
            elif len(buff) > 1:
                dict[th.string] = buff
        return dict

    def _modify_info(self, info):
        info = self._remove_gabage_data(info)

        if '間取り内訳' in info:
            info['間取り内訳'] = re.sub(r'([0-9])([^0-9\.,])', r'\1, \2', unicodedata.normalize('NFKC', info['間取り内訳']).replace(' ', '').replace('、', ', ').replace('・', ', '))
        info['敷金'], info['礼金'] = self._get_deposit_and_keymoney(info['敷金・礼金'], info['家賃'])
        del info['敷金・礼金']
        info['専有面積'] = float(info['専有面積'].rstrip('㎡'))
        if 'バルコニー等面積' in info:
            info['バルコニー等面積'] = float(info['バルコニー等面積'].rstrip('㎡'))

        info = self._modify_builtin_data(info)
        info = self._modify_location_data(info)
        info = self._modify_managefees_data(info)
        info = self._modify_floor_data(info)
        info = self._modify_agent_data(info)
        info = self._modify_transport_data(info)

        info['月額費用'] = self._calc_monthly_cost(info)

        return info

    def _calc_monthly_cost(self, info):
        cost = info['家賃']
        if '管理費' in info:
            cost += info['管理費']
        if '共益費' in info:
            cost += info['共益費']
        return cost

    def _convert_yenstr_to_int(self, raw_str):
        match = re.search(r'[1-9][0-9]*(?:,[0-9]{3})*(?:万(?:[0-9],?[0-9]{3})?)?円', raw_str)
        if match is None:
            return None
        return int(re.sub('([,万円])', '', match.group().replace('万円', '0000')))

    def _convert_monthsstr_to_float(self, raw_str):
        match = re.search(r'([0-9](?:\.[0-9]+)?)(?=ヶ月)', raw_str)
        if match is None:
            return None
        return float(match.group())

    def _get_deposit_and_keymoney(self, raw_str, rent):
        str_ary = raw_str.split('・')
        return self._get_deposit(str_ary[0], rent), self._get_keymoney(str_ary[1], rent)

    def _get_deposit(self, raw_str, rent):
        if raw_str == '敷金なし' or raw_str == '-':
            return 0
        month_result = self._convert_monthsstr_to_float(raw_str)
        if month_result is not None:
            return int(month_result * rent)
        yen_result = self._convert_yenstr_to_int(raw_str)
        if yen_result is not None:
            return yen_result
        raise ValueError(f'Cannot get deposit value: "{raw_str}"')

    def _get_keymoney(self, raw_str, rent):
        if raw_str == '礼金なし' or raw_str == '-':
            return 0
        month_result = self._convert_monthsstr_to_float(raw_str)
        if month_result is not None:
            return int(month_result * rent)
        yen_result = self._convert_yenstr_to_int(raw_str)
        if yen_result is not None:
            return yen_result
        raise ValueError(f'Cannot get keymoney value: "{raw_str}"')

    def _remove_gabage_data(self, info):
        del info['詳細情報']
        return dict((k, v) for (k, v) in info.items() if not isinstance(v, str) or (isinstance(v, str) and v != '-'))

    def _modify_floor_data(self, info):
        if '階数' not in info:
            return info
        loc_floor = re.search(r'[0-9]+(?=階部分)', info['階数'])
        if loc_floor is not None:
            info['位置階数'] = int(loc_floor.group())
        floors = re.search(r'(?<=\()[^\)]+(?=\))', info['階数'])
        if floors is not None:
            info['階数'] = floors.group()
        return info

    def _modify_builtin_data(self, info):
        if '築年月' not in info:
            return info
        info['築年月'] = int(re.sub('[年月]', '', re.sub(r'(?<=[^1])([1-9])(?=月)', r'0\1', info['築年月'])))
        return info

    def _modify_managefees_data(self, info):
        if '管理費等' not in info:
            return info
        if isinstance(info['管理費等'], str):
            info['管理費等'] = [info['管理費等']]

        for value in info['管理費等']:
            if '共益費:' in value:
                if 'なし' in value:
                    info['共益費'] = 0
                else:
                    info['共益費'] = self._convert_yenstr_to_int(value)
            elif '管理費:' in value:
                if 'なし' in value:
                    info['管理費'] = 0
                else:
                    info['管理費'] = self._convert_yenstr_to_int(value)
            elif '円' in value:
                if 'その他月額費' in info:
                    info['その他月額費'].append(value)
                else:
                    info['その他月額費'] = [value]
        del info['管理費等']
        return info

    def _modify_location_data(self, info):
        if '所在地' not in info:
            return info
        if 'search_images/syousai_info_icon.gif' in info['所在地']:
            info['所在地'].remove('search_images/syousai_info_icon.gif')
        if len(info['所在地']) == 2 and 'https://www.google.co.jp/maps?q=' in info['所在地'][0]:
            info['Map'] = info['所在地'][0]
            info['所在地'] = info['所在地'][1]
        return info

    def _modify_agent_data(self, info):
        if len(info['不動産会社詳細']) == 2 and './' in info['不動産会社詳細'][0]:
            info['不動産会社詳細'][0] = 'http://www.fudousan.or.jp/system/' + info['不動産会社詳細'][0].lstrip('./')
        return info

    def _modify_transport_data(self, info):
        if '交通' not in info:
            return info
        if isinstance(info['交通'], str):
            info['交通'] = [info['交通']]

        for train_info in info['交通']:
            train_info = unicodedata.normalize('NFKC', train_info)
            tmp_info = re.sub(r'(?<!徒)歩', '徒歩',
                    re.sub(r'(?<=線 )([^「」]+?)(?=駅 )', r'「\1」',
                        re.sub(r'(?<=[駅])(?=徒?歩)', ' ',
                            re.sub(r'(?<=[^新西六]線)(?! )', ' ', train_info)
                        )
                    )
            )
            if re.search(r'^[^ ]+ ?「[^」 ]+」駅? ?徒歩[0-9]+分$', tmp_info):
                data = re.split('[「」]', tmp_info)
                if '路線' in info:
                    info['路線'].append(data[0].strip())
                else:
                    info['路線'] = [data[0].strip()]
                if '駅徒歩' in info:
                    info['駅徒歩'].append({'駅名': data[1], '時間': int(re.sub('[駅 徒歩分]', '', data[2]))})
                else:
                    info['駅徒歩'] = [{'駅名': data[1], '時間': int(re.sub('[駅 徒歩分]', '', data[2]))}]
            else:
                if 'その他交通' in info:
                    info['その他交通'].append(train_info)
                else:
                    info['その他交通'] = [train_info]
        #del info['交通']
        return info

if __name__ == '__main__':
    sys.exit(main(sys.argv))
