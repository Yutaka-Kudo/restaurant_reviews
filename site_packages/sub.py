from decimal import Decimal
import pykakasi

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
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

OTHER_THAN_RESTAURANTS = [
    # 漫喫ーーーーーーーーーー
    ".*快活CLUB",
    "メディアカフェポパイ",
    "ゲラゲラ",
    # カラオケーーーーーーーーーー
    ".*ビッグエコー",
    ".*BIGECHO",
    ".*JOYSOUND",
    ".*カラオケ コート・ダジュール",
    # "カラオケパセラ",
    ".*カラオケCLUB DAM",
    ".*カラオケ館",
    ".*カラオケONE",
    ".*カラオケの鉄人",
    ".*カラオケ本舗",
    ".*カラオケまねきねこ",
    ".*カラオケマック",
    ".*カラオケ・バンバン",
    ".*カラオケスタジオ",
    ".*カラオケステージ",
    ".*カラオケステーション",
    ".*カラオケセンター",
    ".*カラオケファンタジー",
    ".*カラオケラウンジ",
    ".*カラオケルーム",
    # コンビニーーーーーーーーーー
    "ファミリーマート",
    "ミスタードーナツ",
    "ニューヤマザキデイリーストア",
    "デイリーヤマザキ",
    "ローソン",
    "ミニストップ",
    "セブンイレブン",
    # 不動産ーーーーーーーーーーー
    ".*タウンハウジング",
    ".*株式会社エイブル",
    "ユウキホーム",
    ".*ピタットハウス",
    ".*ハウスコム",
    # デパートーーーーーーーーーー
    "そごう",
    "イトーヨーカドー",
    "西友",
    "髙島屋",
    "日本橋髙島屋",
    "東武百貨店",
    "クイーンズ伊勢丹",
    "ビックカメラ",
    "ヨドバシカメラ",
    "島忠",
    ".*コーナン",
    "シャポー",
    "ラフォーレ",
    "東急プラザ",
    # スーパーーーーーーーーーーー
    "イオン",
    "イオンモール",
    "マックスバリュ",
    "ワイズマート",
    "マルエツ",
    "マミーマート",
    # "IKEA", # IKEA スウェーデンカフェ とかもある
    "ダイエー",
    ".*テンポス",
    "ヤマダデンキ",
    "無印良品",
    "DAISO",
    "ダイソー",
    ".*業務スーパー",
    # ホテルーーーーーーーーーー
    "アパホテル",
    "ホテルリブマックス",
    "ホテルルートイン",
    "アパマンショップ",
    "TOHOシネマズ",
    "スーパーホテル",
    # その他ーーーーーーーーーー
    ".*ティップネス",
    ".*ふなっこ畑",
    ".*銀座惣菜店",
    "メルカート",
    ".*美容室",
    # "",
    # "",
    # "",
]
# .*が付いてないものは商業施設。頭に何も付かないもの限定。つまり施設そのもの。


def chain_replace(store_name: str) -> str:

    chain_dict = {
        "新宿さぼてん": {
            "short": "新宿さぼてん",
            "long": "とんかつ新宿さぼてん"
        },
        "リンガーハット": {
            "short": "リンガーハット",
            "long": "長崎ちゃんぽんリンガーハット"
        },
        "CoCo壱番屋": {
            "short": "CoCo壱番屋",
            "long": "カレーハウスCoCo壱番屋"
        },
        "鳥貴族": {
            "short": "鳥貴族",
            "long": "焼鳥屋 鳥貴族"
        },
        "ちばチャン": {
            "short": "ちばチャン",
            "long": "大衆酒場 ちばチャン"
        },
        "大戸屋": {
            "short": "大戸屋",
            "long": "大戸屋 ごはん処"
        },
        "京ほのか": {
            "short": "京ほのか",
            "long": "完全個室 居酒屋 京ほのか"
        },
        "五右衛門": {
            "short": "五右衛門",
            "long": "洋麺屋五右衛門"
        },
        "ダンダダン酒場": {
            "short": "ダンダダン酒場",
            "long": "肉汁餃子製作所 ダンダダン酒場"
        },
        "ミライザカ": {
            "short": "ミライザカ",
            "long": "旨唐揚げと居酒メシ ミライザカ"
        },
        "すたみな太郎NEXT": {
            "short": "すたみな太郎NEXT",
            "long": "食べ放題・バイキング すたみな太郎NEXT"
        },
        "くら寿司": {
            "short": "くら寿司",
            "long": "無添くら寿司"
        },
        "つぼ八": {
            "short": "つぼ八",
            "long": "北海道の恵み つぼ八"
        },
        "フレッシュネスバーガー": {
            "short": "フレッシュネスバーガー",
            "long": "FRESHNESS BURGER（フレッシュネスバーガー）"
        },
        "千年の宴": {
            "short": "千年の宴",
            "long": "個室空間 湯葉豆腐料理 千年の宴"
        },
        "はなの舞": {
            "short": "はなの舞",
            "long": "海鮮居酒屋 はなの舞"
        },
        "とりいちず": {
            "short": "とりいちず",
            "long": "水炊き・焼鳥・鶏餃子 とりいちず"
        },
        "酔っ手羽": {
            "short": "酔っ手羽",
            "long": "居酒屋革命酔っ手羽"
        },
        "博多劇場": {
            "short": "博多劇場",
            "long": "屋台屋 博多劇場"
        },
        "甘太郎": {
            "short": "甘太郎",
            "long": "手作り居酒屋 甘太郎"
        },
        "四六時中": {
            "short": "四六時中",
            "long": "おひつごはん四六時中"
        },
        "すた丼": {
            "short": "元祖すた丼の店",
            "long": "伝説のすた丼屋"
        },
        "ポポラマーマ": {
            "short": "ポポラマーマ",
            "long": "ゆであげ生パスタ ポポラマーマ"
        },
        "ブロンコビリー": {
            "short": "ブロンコビリー",
            "long": "ステーキハウス ブロンコビリー"
        },
        "HUB": {
            "short": "HUB",
            "long": "BRITISH PUB HUB"
        },
        "牛角": {
            "short": "牛角",
            "long": "炭火焼肉酒家 牛角"
        },
        "忍家": {
            "short": "全席個室居酒屋 忍家",
            "long": "全席個室ダイニング 忍家"
        },
        "木曽路": {
            "short": "木曽路",
            "long": "しゃぶしゃぶ 日本料理 木曽路"
        },
        "さくら水産": {
            "short": "さくら水産",
            "long": "産物居酒屋 さくら水産"
        },
        "楽蔵": {
            "short": "楽蔵",
            "long": "全席個室 楽蔵"
        },
        "北海道": {
            "short": "北海道",
            "long": "北の味紀行と地酒 北海道"
        },
        "ありがとう": {
            "short": "ありがとう",
            "long": "みんなの居酒屋ありがとう"
        },
        "ダンダダン": {
            "short": "ダンダダン酒場",
            "long": "肉汁餃子のダンダダン"
        },
        "ディプント": {
            "short": "ワインの酒場 ディプント",
            "long": "ワインの酒場。ディプント"
        },
        "銀座ライオン": {
            "short": "銀座ライオン",
            "long": "ビアホール銀座ライオン"
        },
        "とんでん": {
            "short": "和食レストランとんでん",
            "long": "北海道生まれ和食処とんでん"
        },
        "扇屋": {
            "short": "扇屋",
            "long": "やきとりの扇屋"
        },
        "いきなり": {
            "short": "いきなりステーキ",
            "long": "いきなり！ステーキ"
        },
        # "": {
        #     "short": "",
        #     "long": ""
        # },
    }

    store_name = store_name.replace(' ', '')
    # chain_dict keyを回して該当するかチェック
    hit = [s for s in chain_dict.keys() if s.replace(' ', '') in store_name]
    if len(hit) == 1:
        hit = hit[0]  # リスト解除
        if chain_dict[hit]["long"].replace(' ', '') in store_name:  # 先に長い名前から当てはめる
            replaced_name = store_name.replace(chain_dict[hit]["long"].replace(' ', ''), chain_dict[hit]["short"].replace(' ', ''))
        elif chain_dict[hit]["short"].replace(' ', '') in store_name:
            replaced_name = store_name.replace(chain_dict[hit]["short"].replace(' ', ''), chain_dict[hit]["long"].replace(' ', ''))
        else:
            replaced_name = ""
        return replaced_name
    else:
        return None


def category_set(store_obj, category_list, errorlist=None):
    # カテゴリ登録
    try:
        attrs = [
            "category1",
            "category2",
            "category3"
        ]
        for i, category in enumerate(category_list):
            setattr(store_obj, attrs[i], category)
        store_obj.save()

    except Exception as e:
        print(f'カテゴリ登録failed.. {e}')
        if errorlist:
            errorlist.append((type(e), e, category_list))


def name_set(store_obj: models.Store, store_name: str, media_type: str, yomigana: str = "", yomi_roma: str = ""):

    store_obj.update_name(store_name, media_type)

    if media_type == "tb" and (yomigana or yomi_roma):  # 食べログの名前を正式名称にする
        store_obj.update_name(store_name)

    if (yomigana and media_type == "tb") or (yomigana and media_type == "gn" and not store_obj.yomigana):
        store_obj.yomigana = yomigana
        store_obj.save()
    # elif not store_obj.yomigana:
    #     kakasi = pykakasi.kakasi()
    #     name_hira = kakasi.convert(store_name.strip().replace(' ', ''))
    #     name_hira = "".join([s["hira"] for s in name_hira])
    #     store_obj.yomigana = name_hira
    #     store_obj.save()

    if (yomi_roma and media_type == "tb") or (yomi_roma and media_type == "gn" and not store_obj.yomi_roma):
        store_obj.yomi_roma = yomi_roma
        store_obj.save()
    # elif not store_obj.yomi_roma:
    #     kakasi = pykakasi.kakasi()
    #     name_roma = kakasi.convert(store_name.strip().replace(' ', ''))
    #     name_roma = "".join([s["hepburn"] for s in name_roma])
    #     store_obj.yomi_roma = name_roma
    #     store_obj.save()


def address_set(store_obj, address, media_type):
    if (address and not store_obj.address) or (address and media_type == "gn") or (address and media_type == "tb"):
        store_obj.address = address
        store_obj.save()


def setTotalRateForStore(store_md) -> float:
    rate_md = [md for md in store_md if md.media_type.__str__() in ["gn", "google", "tb", "uber"]]
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
    return total_rate
