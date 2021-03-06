# 不動産ジャパンの検索インタフェース

## URIパラメータ
"`http://www.fudousan.or.jp/system/?`"に続けて設定する。

### act=${VALUE}
画面モード

値 | 説明
-|-
d | 物件詳細
l | リスト表示
f | 条件設定
m | 都道府県選択

### type=${VALUE}
物件種別

値 | 説明
-|-
31 | 賃貸マンション・アパート
32 | 賃貸一戸建て・その他
33 | 賃貸事業用物件（事務所・店舗など）

### stype=${VALUE}
検索絞り込み方法

値 | 説明
-|-
l | エリアから検索
r | 路線から検索
d | 詳細検索

### pref=${VALUE}
都道府県

値 | 説明
-|-
13 | 東京
... | ...

### city[]=${VALUE}
区市町村(エリアから検索時)

値 | 説明
-|-
13101 | 千代田区
13117 | 北区
... | ...

### town[]=${VALUE}
町丁名(エリアから検索時)

値 | 説明
-|-
13101019001 | 神田神保町１丁目(千代田区)
13117001001 | 赤羽１丁目(北区)
... | ...

### line[]=${VALUE}
路線(路線から検索時)

値 | 説明
-|-
2172 | 山手線
2196 | 京浜東北・根岸線
... | ...

### eki[]=${VALUE}
駅(路線から検索時)

値 | 説明
-|-
2172010 | 東京駅(山手線)
2196210 | 東京駅(京浜東北・根岸線)
... | ...

### p=${NUM}
ページ数(1〜)

### n=${VALUE}
1ページあたりの件数

値 | 説明
-|-
20 | 20件表示
50 | 50件表示
100 | 100件表示

### s=${VALUE}
検索結果の並び替え

値 | 説明
-|-
n | 新着
s | 所在地
rh | 賃料 高い
rl | 賃料 低い
auh | 専有面積 広い
aul | 専有面積 狭い
cn | 築年月 新しい
co | 築年月 古い

### v=${VALUE}
検索結果の画像表示

値 | 説明
-|-
on | 画像あり
off | 画像なし

### bid=${ID}
物件番号(ID)

### org=${VALUE}
情報提供会社所属組織

値 | 説明
-|-
ZT | 全国宅地建物取引業協会連合会
FR | 不動産流通経営協会
ZN | 全日本不動産協会
? | 全国住宅産業協会

### rl=${VALUE}
最低賃料

値 | 説明
-|-
l | 下限なし
40 | 4万以上
45 | 4.5万以上
50 | 5万以上
... | ...
195 | 19.5万以上
200 | 20万以上

### rh=${VALUE}
最高賃料

値 | 説明
-|-
h | 上限なし
40 | 4万未満
45 | 4.5万未満
50 | 5万未満
... | ...
195 | 19.5万未満
200 | 20万未満

### asl=${VALUE}
最低専有面積

値 | 説明
-|-
l | 下限なし
20 | 20平米以上
40 | 40平米以上
50 | 50平米以上
60 | 60平米以上
70 | 70平米以上
80 | 80平米以上
90 | 90平米以上
100 | 100平米以上
120 | 120平米以上
150 | 150平米以上

### ash=${VALUE}
最高専有面積

値 | 説明
-|-
h | 上限なし
20 | 20平米未満
40 | 40平米未満
50 | 50平米未満
60 | 60平米未満
70 | 70平米未満
80 | 80平米未満
90 | 90平米未満
100 | 100平米未満
120 | 120平米未満
150 | 150平米未満


### yc=${VALUE}
築年数

値 | 説明
-|-
1 | 新築
3 | 3年以内
5 | 5年以内
10 | 10年以内
15 | 15年以内

### th=${VALUE}
最寄駅徒歩分

値 | 説明
-|-
5 | 5分以内
10 | 10分以内
15 | 15分以内

### md[]=${VALUE}
間取り

値 | 説明
-|-
1 | 1R・1K・1DK
2 | 1LDK・2K・2DK
3 | 2LDK・3K・3DK
4 | 3LDK・4K・4DK
5 | 4LDK以上

### 基本検索条件

オプション | 説明
-|-
ta=1 | アパート検索
tm=1 | マンション検索
rik=1 | 管理費・共益費なし
rnr=1 | 礼金なし
rns=1 | 敷金なし
gz=1 | 画像あり
zm=1 | 図面あり

### op[]=${VALUE}
こだわり検索条件  
重ねがけ可能

値 | 説明
-|-
d501 | 空き家バンク
d785 | シェアハウス
d786 | DIY可
d787 | BELS/省エネ基準適合認定
os | 1階のみ
ts | 2階以上のみ
so | 南向き
d332 | 角部屋
d344 | 最上階
ac | エアコン
bt | バス・トイレ別
oi | 追い焚き機能あり
wa | 洗濯機置場あり
pe | ペット可・相談
im | 楽器可・相談
d315 | 女性限定
d334 | フリーレント
fl | フローリング
lf | ロフト付
bl | バルコニー付
al | オートロック
mi | TVモニタ付インターホン
in | インターネット可
ca | CATV
bs | BS
cs | CS
el | エレベーター
cp | 駐車場あり
bp | 駐輪場あり
d227 | 都市ガス
d300 | 宅配ボックス
d341 | 24時間換気システム
d292 | 専用庭
d275 | 室内洗濯機置場
d278 | 浴室乾燥機
d342 | 24時間セキュリティ
d238 | 床暖房
d324 | バリアフリー
d325 | メゾネット
d337 | 二世帯向き

## Example
- 東京都北区で家賃7万以上9万未満のマンション、20平米以上の1R・1K・1DK、バス・トイレ別でフローリングの物件を専有面積が広い順で50件ずつリスト表示
	- `http://www.fudousan.or.jp/system/?act=l&type=31&tm=1&stype=d&pref=13&city[]=13117&rl=70&rh=90&asl=20&ash=h&md[]=1&op[]=bt&op[]=fl&s=auh&n=50`
- 東京駅の賃貸マンション・アパートをリスト表示
	- `http://www.fudousan.or.jp/system/?act=l&type=31&stype=d&pref=13&line[]=2172&eki[]=2172010`
- 東京のある物件の詳細表示
	- `http://www.fudousan.or.jp/system/?act=d&type=31&bid=00000000&org=ZT`

