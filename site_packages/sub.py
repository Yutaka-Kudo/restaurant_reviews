from decimal import Decimal
import pykakasi
import re

from scrape import models


IGNORE_STORE_NAME = [
    "お台場たこ焼きミュージアム",
    "ふなばしアンデルセン公園",
    "千葉ポートタワー",
    "オークラ千葉ホテル",
    # "三井ガーデンホテル千葉",
    "株式会社ダイニングイノベーション",
    "恵比寿ガーデンプレイスタワー",
    "カラオケ レインボー 浅草店",
    "カラオケ ASO：VIBA！",
    "たくみ稜のカラオケ音楽舘",
    "からおけ屋 練馬店",
    "カラオケトマト 練馬店",
    "千日前本店",
    "APAホテル 東京板橋",
    "センチュリオンホテル上野",
    "ダイワロイネットホテル 東京赤羽",
    "フランス料理 帝国ホテル",
    "ホテルウィングインターナショナル東京赤羽",
    "ホテルバリアンリゾート千葉中央店",
    "ホテルミッドイン 赤羽駅前",
    "ホテルライフツリー上野（BBHホテルグループ）",
    "ロイヤルパインズホテル浦和",
    "京成ホテルミラマーレ",
    "第一ホテル東京",
    "銚子かもめホテル",
    "龍宮城スパホテル三日月",
    "(株)フジオフードシステム",
    "厨房",
    "露天神社(お初天神)",
    "泉の広場",
    "株式会社サン・アクト",
    "ウオッセ21",
    "犬吠テラステラス",
    "犬吠埼",
    "犬吠埼灯台",
    "犬吠埼温泉 ぎょうけい館",
    "犬吠館",
    "原宿アルタ",
    "AKIBA ICHI",
    "UDX",
    "アキバ・トリム",
    "ペリエ千葉",
    "山崎文庫",
    "株式会社グローバルダイニング",
    "（有）ベル スナック",
    "渋谷横丁",
    "原宿竹下通り 商店会",
    "スヌーピータウンショップ原宿店",
    "ファミリーオ館山",
    "ベニバナウォーク 桶川",
    "東京ドームシティ",
    "スパ ラクーア",
    "ミーツポート",
    "鎌倉館",
    "自由が丘デパート",
    "(株)アシスト自由が丘店",
    "コンテナキッチン",
    "ネクスト船橋",
    "東京ベイ幕張ホール",
    "船橋競馬場",
    "飲食店",
    "HACOSTADIUM TOKYO.one",
    "ハコプラス",
    "市川サンライズゴルフセンター",
    "ニッケコルトンプラザ",
    "津田沼PARCO",
    "まんが＆インターネットカフェ アルファ24 京成大久保店",
    "ペリエ津田沼",
    "おけがわマイン",
    "大宮高島屋",
    "L'UENO（ルエノ）",
    "",
    "",
    "",
    "",
]

OTHER_THAN_RESTAURANTS = [
    ".*駅$",
    # 漫喫ーーーーーーーーーー
    ".*快活CLUB",
    ".*快活クラブ",
    "メディアカフェポパイ",
    "ゲラゲラ",
    "まんが喫茶",
    "マンガ喫茶",
    # カラオケーーーーーーーーーー
    ".*歌うんだ村",
    ".*カラオケ館",
    ".*カラオケCLUB DAM",
    ".*カラオケシティベア",
    ".*カラオケスタジオ",
    ".*カラオケステージ",
    ".*カラオケステーション",
    ".*カラオケセンター",
    ".*カラオケの鉄人",
    ".*カラオケ・バンバン",
    ".*カラオケBanBan",
    ".*カラオケパセラ",
    ".*カラオケファンタジー",
    ".*カラオケ本舗",
    ".*カラオケまねきねこ",
    ".*カラオケマック",
    ".*カラオケラウンジ",
    ".*カラオケルーム",
    ".*カラオケONE",
    ".*コート・ダジュール",
    ".*スーパーカラオケ",
    ".*JOYSOUND",
    "ひとりカラオケ",
    ".*ビッグエコー",
    ".*BIGECHO",
    # 不動産ーーーーーーーーーーー
    "アパマンショップ",
    ".*タウンハウジング",
    ".*株式会社エイブル",
    "ユウキホーム",
    ".*ピタットハウス",
    ".*ハウスコム",
    # コンビニーーーーーーーーーー
    "セブンイレブン",
    "セブン-イレブン",
    "デイリーヤマザキ",
    "ナチュナルローソン",
    "ニューヤマザキデイリーストア",
    "NewDays",
    "ニューデイズ",
    "ファミリーマート",
    "ミスタードーナツ",
    "ミニストップ",
    "ローソン",
    "ナチュラルローソン",
    # 複合施設ーーーーーーーーーーー
    "アトレ",
    "エキュート",
    "シャポー",
    "三井アウトレットパーク",
    "LUMINE",
    "ルミネ",
    # デパートーーーーーーーーーー
    "伊勢丹",
    "イトーヨーカドー",
    "小田急百貨店",
    "クイーンズ伊勢丹",
    "京王百貨店",
    "西武",
    "そごう",
    "髙島屋",
    "東武百貨店",
    "東急百貨店",
    "東急プラザ",
    "東急ストア",
    "日本橋髙島屋",
    "松坂屋",
    "ラフォーレ",
    # スーパーーーーーーーーーーー
    "イオン",
    "イオンモール",
    "カスミ",
    ".*業務スーパー",
    # "IKEA", # IKEA スウェーデンカフェ とかもある
    "コープ",
    "さわみつ青果",
    "成城石井",
    "西友",
    "ダイエー",
    "ニュークイック",
    "ニュー・クイック",
    "ベルク",
    "マックスバリュ",
    "マルエツ",
    "マミーマート",
    "ヨークマート",
    "ワイズマート",
    # ホテルーーーーーーーーーー
    "アパホテル",
    "スーパーホテル",
    "東横INN",
    "ドーミーイン",
    "ホテルリブマックス",
    "ホテルルートイン",
    "ロイヤルパインズホテル",
    # その他ーーーーーーーーーー
    "カインズ",
    "キャンドゥ",
    ".*銀座惣菜店",
    ".*コーナン",
    "島忠",
    "100円ショップ シルク",
    "ダイソー",
    "DAISO",
    ".*ティップネス",
    ".*テンポス",
    "TOHOシネマズ",
    ".*美容室",
    "ビックカメラ",
    ".*ふなっこ畑",
    "無印良品",
    "メルカート",
    "ヤマダデンキ",
    "ヨドバシカメラ",
]
# .*が付いてないものは商業施設。頭に何も付かないもの限定。つまり施設そのもの。


def chain_replace(store_name: str) -> list:

    chain_dict = {
        "青葉": [
            "青葉",
            "牛たんと和牛焼き 青葉",
        ],
        "揚州商人": [
            "揚州商人",
            "中国ラーメン揚州商人",
        ],
        "甘太郎": [
            "甘太郎",
            "手作り居酒屋 甘太郎",
        ],
        "ありがとう": [
            "ありがとう",
            "みんなの居酒屋ありがとう",
        ],
        "いきなり": [
            "いきなりステーキ",
            "いきなり！ステーキ",
        ],
        "UOKIN": [
            "UOKIN",
            "イタリアンバル UOKIN",
        ],
        "魚がし日本一": [
            "魚がし日本一",
            "寿司 魚がし日本一",
        ],
        "宇奈とと": [
            "宇奈とと",
            "名代 宇奈とと",
        ],
        "エノテカ": [
            "エノテカ",
            "ワインショップ・エノテカ",
        ],
        "扇屋": [
            "扇屋",
            "やきとりの扇屋",
        ],
        "温野菜": [
            "温野菜",
            "しゃぶしゃぶ温野菜",
        ],
        "大戸屋": [
            "大戸屋",
            "大戸屋 ごはん処",
        ],
        "カフェベローチェ": [
            "カフェベローチェ",
            "カフェ・ベローチェ",
        ],
        "がブリチキン。": [
            "がブリチキン。",
            "骨付鳥・からあげ・ハイボール がブリチキン。",
        ],
        "壁の穴": [
            "壁の穴",
            "パスタ & ピザ 壁の穴",
        ],
        "かまどか": [
            "かまどか",
            "肉料理 和食 土鍋めし かまどか",
            "熟成焼鳥 居酒屋 かまどか",
        ],
        "木曽路": [
            "木曽路",
            "しゃぶしゃぶ 日本料理 木曽路",
        ],
        "北の家族": [
            "北の家族",
            "北海道酒場 北の家族",
        ],
        "牛角": [
            "牛角",
            "炭火焼肉酒家 牛角",
            "炭火焼肉 牛角",
            "焼肉酒家 牛角",
        ],
        "牛繁": [
            "牛繁",
            "食べ放題 元氣七輪焼肉 牛繁",
        ],
        "京ほのか": [
            "京ほのか",
            "完全個室 居酒屋 京ほのか",
        ],
        "京都勝牛": [
            "京都勝牛",
            "牛カツ京都勝牛",
        ],
        "きんちゃん家": [
            "きんちゃん家",
            "50えん焼とりきんちゃん家",
        ],
        "金の蔵": [
            "金の蔵",
            "きんくら酒場 金の蔵",
        ],
        "九州じゃんがら": [
            "九州じゃんがら",
            "九州じゃんがららあめん",
        ],
        "くら寿司": [
            "くら寿司",
            "無添くら寿司",
        ],
        "玄品": [
            "玄品",
            "ふぐ料理 玄品",
            "玄品 ふぐ・かに料理",
        ],
        "神戸屋": [
            "神戸屋",
            "フレッシュベーカリー神戸屋",
        ],
        "五右衛門": [
            "五右衛門",
            "洋麺屋五右衛門",
        ],
        "CoCo壱番屋": [
            "CoCo壱番屋",
            "カレーハウスCoCo壱番屋",
        ],
        "CONA": [
            "CONA",
            "イタリアン＆ワインバー CONA",
        ],
        "コメダ珈琲店": [
            "コメダ珈琲店",
            "珈琲所 コメダ珈琲店",
        ],
        "KollaBo": [
            "炭火焼肉・韓国料理 KollaBo",
            "炭火焼肉・韓国料理 KollaBo(コラボ)",
            "焼肉・韓国料理 KollaBo",
            "焼肉・韓国料理 KollaBo(コラボ)",
            "炭火焼肉・韓国料理 KollaBo",
            "炭火焼肉・韓国料理 KollaBo(コラボ)",
            "炭火焼肉・韓国料理 KollaBo （コラボ）",
        ],
        "さかなや道場": [
            "さかなや道場",
            "個室 まぐろ居酒屋 さかなや道場",
        ],
        "さくら水産": [
            "さくら水産",
            "海産物居酒屋 さくら水産",
        ],
        "忍家": [
            "全席個室居酒屋 忍家",
            "全席個室ダイニング 忍家",
        ],
        "さぼてん": [
            "新宿さぼてん",
            "新宿とんかつ さぼてん",
            "新宿さぼてんデリカ",
            "とんかつ新宿さぼてん",
            "とんかつ新宿さぼてんデリカ",
        ],
        "SCHMATZ": [
            "SCHMATZ",
            "クラフトビールダイニング SCHMATZ ‐シュマッツ‐",
        ],
        "四六時中": [
            "四六時中",
            "おひつごはん四六時中",
        ],
        "白木屋": [
            "白木屋",
            "居楽屋白木屋",
        ],
        "スズカフェ": [
            "スズカフェ",
            "SUZU CAFE",
        ],
        "SUZU CAFE": [
            "スズカフェ",
            "SUZU CAFE",
        ],
        "すたみな太郎NEXT": [
            "すたみな太郎NEXT",
            "食べ放題・バイキング すたみな太郎NEXT",
        ],
        "すた丼": [
            "元祖すた丼の店",
            "伝説のすた丼屋",
            "名物すた丼の店",
        ],
        "スターバックス": [
            "スターバックス",
            "スターバックス・コーヒー",
            "スターバックス コーヒー",
            "Starbucks Coffee",
        ],
        "Starbucks Coffee": [
            "Starbucks Coffee",
            "スターバックス コーヒー",
            "スターバックス・コーヒー",
        ],
        "千年の宴": [
            "千年の宴",
            "個室空間 湯葉豆腐料理 千年の宴",
        ],
        "鶏ヤロー": [
            "それゆけ!鶏ヤロー!",
            "それゆけ！鶏ヤロー",
            "それゆけ 鶏ヤロー",
            "居酒屋それゆけ！鶏ヤロー！",
            "時間無制限食べ飲み放題2000円酒場 それゆけ！鶏ヤロー",
        ],
        "大吉": [
            "大吉",
            "やきとり大吉",
        ],
        "ダッキーダック": [
            "ダッキーダック",
            "オムライス・ケーキ ダッキーダック",
        ],
        "タリーズコーヒー": [
            "タリーズコーヒー",
            "TULLY’S COFFEE",
        ],
        "TULLY’S COFFEE": [
            "タリーズコーヒー",
            "TULLY’S COFFEE",
        ],
        "ダンダダン": [
            "ダンダダン酒場",
            "肉汁餃子のダンダダン",
            "肉汁餃子製作所 ダンダダン酒場",
        ],
        "ちばチャン": [
            "ちばチャン",
            "大衆酒場 ちばチャン",
        ],
        "つな八": [
            "つな八",
            "新宿つな八",
            "天ぷら新宿つな八",
        ],
        "つぼ八": [
            "つぼ八",
            "北海道の恵み つぼ八",
        ],
        "ディプント": [
            "ワイン酒場 ディプント",
            "ワインの酒場 ディプント",
            "ワインの酒場。ディプント",
        ],
        "Di PUNTO": [
            "ワイン酒場 ディプント",
            "ワインの酒場 ディプント",
            "ワインの酒場。ディプント",
        ],
        "東京油組総本店": [
            "東京油組総本店",
            "油そば 東京油組総本店",
        ],
        "トラジ": [
            "トラジ",
            "焼肉トラジ",
        ],
        "とりいちず": [
            "とりいちず",
            "とりいちず酒場",
            "水炊き 焼鳥 とりいちず酒場",
            "水炊き・焼鳥 とりいちず酒場",
            "水炊き・焼き鳥 とりいちず",
            "水炊き・焼き鳥 とりいちず酒場",
            "水炊き・焼鳥・鶏餃子 とりいちず",
        ],
        "鳥貴族": [
            "鳥貴族",
            "焼鳥屋 鳥貴族",
        ],
        "土間土間": [
            "土間土間",
            "居酒家土間土間",
            "居酒屋 土間土間",
            "大人の隠れ家個室 土間土間",
            "いつでも199円（税込）生ビール土間土間",
            "いつでも190円生ビール 創作居酒屋 土間土間",
        ],
        "とんでん": [
            "和食レストランとんでん",
            "北海道生まれ和食処とんでん",
        ],
        "どん亭": [
            "どん亭",
            "しゃぶしゃぶどん亭",
        ],
        "nana’s green tea": [
            "nana’s green tea",
            "ナナズグリーンティー",
        ],
        "肉屋の台所": [
            "肉屋の台所",
            "和牛焼肉食べ放題 肉屋の台所",
        ],
        "馬車道": [
            "馬車道",
            "レストラン馬車道",
        ],
        "ハーブス": [
            "ハーブス",
            "HARBS",
        ],
        "HARBS": [
            "ハーブス",
            "HARBS",
        ],
        "HUB": [
            "HUB",
            "BRITISH PUB HUB",
        ],
        "バグース": [
            "バグース",
            "BAGUS",
            "BAGUS－バグース－",
        ],
        "BAGUS": [
            "バグース",
            "BAGUS",
            "BAGUS－バグース－",
        ],
        "はなの舞": [
            "はなの舞",
            "海鮮居酒屋 はなの舞",
        ],
        "博多劇場": [
            "博多劇場",
            "屋台屋 博多劇場",
        ],
        "ふたご": [
            "ふたご",
            "大阪焼肉 ホルモン ふたご",
        ],
        "フレッシュネスバーガー": [
            "フレッシュネスバーガー",
            "FRESHNESS BURGER（フレッシュネスバーガー）",
        ],
        "ブロンコビリー": [
            "ブロンコビリー",
            "ステーキハウス ブロンコビリー",
        ],
        "プロント": [
            "プロント",
            "プロント PRONTO",
            "PRONTO",
        ],
        "PRONTO": [
            "PRONTO",
            "プロント PRONTO",
            "プロント",
        ],
        "ベックスコーヒーショップ": [
            "ベックスコーヒーショップ",
            "BECK’S COFFEE SHOP(ベックスコーヒーショップ)",
        ],
        "北海道": [
            "北海道",
            "北の味紀行と地酒 北海道",
        ],
        "ポポラマーマ": [
            "ポポラマーマ",
            "ゆであげ生パスタ ポポラマーマ",
        ],
        "三田製麺所": [
            "三田製麺所",
            "つけ麺専門店 三田製麺所",
        ],
        "美登利": [
            "梅丘寿司の美登利総本店",
            "梅丘 寿司の美登利",
        ],
        "ミライザカ": [
            "ミライザカ",
            "旨唐揚げと居酒メシ ミライザカ",
        ],
        "モミアンドトイズ": [
            "モミアンドトイズ",
            "MOMI&TOY'S",
        ],
        "MOMI&TOY'S": [
            "MOMI&TOY'S",
            "モミアンドトイズ",
        ],
        "山田うどん": [
            "山田うどん",
            "山田うどん食堂",
            "ファミリー食堂 山田うどん食堂",
        ],
        "やまと": [
            "焼肉やまと",
            "A5黒毛和牛焼肉 やまと",
        ],
        "酔っ手羽": [
            "酔っ手羽",
            "居酒屋革命酔っ手羽",
        ],
        "ライオン": [
            "ライオン",
            "銀座ライオン",
            "銀座ライオンLEO",
            "ビアホール銀座ライオン",
            "ビヤホール 銀座ライオン",
            "ビヤレストラン　銀座ライオン",
            "ビヤ＆ワイングリル銀座ライオン",
            "ビール＆ワイン グリル銀座ライオン",
        ],
        "楽蔵": [
            "楽蔵",
            "全席個室 楽蔵",
            "全席個室 楽蔵‐RAKUZO‐",
        ],
        "パウザ": [
            "ラパウザ",
            "ラ・パウザ",
            "ゆであげパスタ＆ピザ　ラ・パウザ",
            "ゆであげパスタ＆焼き上げピザ ラパウザ",
        ],
        "リンガーハット": [
            "リンガーハット",
            "長崎ちゃんぽんリンガーハット",
        ],
        "和幸": [
            "和幸",
            "とんかつ和幸",
        ],
        "わん": [
            "わん",
            "くいもの屋 わん",
            "くいもん屋 わん",
        ],
    }

    def replace_space(name: str):
        return name.replace(' ', '').replace('　', '')

    chain_dict = {k: v for k, v in chain_dict.items() if k}  # 空除去
    store_name = replace_space(store_name)
    # chain_dict keyを回して該当するかチェック
    key = [k for k in chain_dict.keys() if replace_space(k) in store_name]
    if len(key) == 1:
        key = key[0]  # リスト解除
        kouho_list: list = chain_dict[key]
        kouho_list = [replace_space(name) for name in kouho_list]
        try:
            hit_sentence = max([re.match(s, store_name).group() for s in kouho_list if re.match(s, store_name)])
            kouho_list.remove(hit_sentence)  # あるやつは除外してメモリ節約

            return [store_name.replace(hit_sentence, kouho) for kouho in kouho_list]

        except Exception:
            return []

        # key = key[0]  # リスト解除
        # if chain_dict[key]["long"].replace(' ', '').replace('　','') in store_name:  # 先に長い名前から当てはめる
        #     replaced_name = store_name.replace(chain_dict[key]["long"].replace(' ', '').replace('　',''), chain_dict[key]["short"].replace(' ', '').replace('　',''))
        # elif chain_dict[key]["short"].replace(' ', '').replace('　','') in store_name:
        #     replaced_name = store_name.replace(chain_dict[key]["short"].replace(' ', '').replace('　',''), chain_dict[key]["long"].replace(' ', '').replace('　',''))
        # else:
        #     replaced_name = ""
        # return replaced_name
    else:
        return []


def set_category(st_obj, category_list):
    # カテゴリ登録
    try:
        attrs = [
            "category1",
            "category2",
            "category3"
        ]
        for i, category in enumerate(category_list):
            setattr(st_obj, attrs[i], category)
        st_obj.save()

    except Exception as e:
        print(f'カテゴリ登録failed.. {e}')


def set_name(st_obj: models.Store, store_name: str, mt_str: str, yomigana: str = "", yomi_roma: str = ""):

    if getattr(st_obj, f"store_name_{mt_str}") != store_name:
        st_obj.update_name(store_name, mt_str)

    if mt_str == "tb" and (yomigana or yomi_roma):  # 読み仮名をもっている自信のある食べログなら正式名称にする
        if getattr(st_obj, "store_name") != store_name:
            st_obj.update_name(store_name)

    # よみがなーーーーーーーーーーー
    if (yomigana and mt_str == "tb") or (yomigana and mt_str == "gn" and not st_obj.yomigana):
        if getattr(st_obj, "yomigana") != yomigana:
            st_obj.yomigana = yomigana
            st_obj.save()
    elif (mt_str == "google" and not st_obj.yomigana):
        kakasi = pykakasi.kakasi()
        conv = kakasi.convert(st_obj.store_name)
        st_obj.yomigana = "".join([s["hira"] for s in conv]).strip().replace(' ', '').replace('　', '')[:99]
        st_obj.save()

    # よみローマーーーーーーーーーーーー
    if (yomi_roma and mt_str == "tb") or (yomi_roma and mt_str == "gn" and not st_obj.yomi_roma):
        if getattr(st_obj, "yomi_roma") != yomi_roma:
            st_obj.yomi_roma = yomi_roma
            st_obj.save()
    elif (mt_str == "google" and not st_obj.yomi_roma):
        kakasi = pykakasi.kakasi()
        if st_obj.yomigana:
            conv = kakasi.convert(st_obj.yomigana)
        else:
            conv = kakasi.convert(st_obj.store_name)
        st_obj.yomi_roma = "".join([s["hepburn"] for s in conv]).strip().replace(' ', '').replace('　', '')[:99]
        st_obj.save()


def set_address(st_obj, address, mt_str):
    if (address and not st_obj.address) or (address and mt_str == "gn") or (address and mt_str == "tb"):
        if getattr(st_obj, "address") != address:
            st_obj.address = address
            st_obj.save()


def setTotalRateForStore(store_md) -> float:
    rate_md, uber_md = [], None
    for md in store_md:
        if md.media_type.__str__() in ["gn", "google", "tb"]:
            rate_md.append(md)
        elif md.media_type.__str__() in ["uber"]:
            uber_md = md

    if rate_md:
        rate_list, total_review_count = [], []
        for md in rate_md:
            if md.media_type.__str__() == "tb":  # 食べログ補正
                rate = md.rate + ((md.rate - Decimal("2.5")) * Decimal(".6"))
            else:
                rate = md.rate
            if md.review_count:
                rate_list.append(rate * md.review_count)
                total_review_count.append(md.review_count)
        try:
            total_rate = sum(rate_list) / sum(total_review_count)
        except ZeroDivisionError:
            total_rate = 0

        # uberは基準点4.5からの差分×(件数200＝100％)を加える
        if uber_md:
            if uber_md.rate:
                add_rate = (uber_md.rate - Decimal("4.5")) * Decimal((uber_md.review_count / (200 / 100)) * 0.01)  # ((件数/(最大件数を100で割った割合))*％割合)
                total_rate += add_rate
    else:
        total_rate = 0

    return total_rate


def deleteAndAddClosedname(name, area1, area2):
    models.Store.objects.get(store_name=name, area__area_name=f"{area1} {area2}").delete()
    # 既存のファイルの末尾が改行になってるか
    try:
        with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "r") as f:
            lines = f.readlines()
        reads = lines[-1][-1]
        formated_lines = [line.strip() for line in lines]
    except Exception:
        reads = "\n"
        formated_lines = []
    with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "a") as f:
        if name not in formated_lines:
            if reads == "\n":
                f.write(name)
            else:
                f.write("\n")
                f.write(name)
            print('closed_list作成')
        else:
            print('すでにありました。')
