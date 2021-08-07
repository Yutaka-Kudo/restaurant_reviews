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
    "",
    "",
    "",
    "",
    "",
]

OTHER_THAN_RESTAURANTS = [
    # 漫喫ーーーーーーーーーー
    ".*快活CLUB",
    ".*快活クラブ",
    "メディアカフェポパイ",
    "ゲラゲラ",
    # カラオケーーーーーーーーーー
    ".*歌うんだ村",
    ".*カラオケ館",
    ".*カラオケCLUB DAM",
    ".*カラオケ コート・ダジュール",
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
    "デイリーヤマザキ",
    "ナチュナルローソン",
    "ニューヤマザキデイリーストア",
    "NewDays",
    "ニューデイズ",
    "ファミリーマート",
    "ミスタードーナツ",
    "ミニストップ",
    "ローソン",
    # 複合施設ーーーーーーーーーーー
    "アトレ",
    "エキュート",
    "シャポー",
    "三井アウトレットパーク",
    # デパートーーーーーーーーーー
    "伊勢丹",
    "イトーヨーカドー",
    "クイーンズ伊勢丹",
    "そごう",
    "髙島屋",
    "東武百貨店",
    "東急プラザ",
    "日本橋髙島屋",
    "ラフォーレ",
    # スーパーーーーーーーーーーー
    "イオン",
    "イオンモール",
    "カスミ",
    ".*業務スーパー",
    # "IKEA", # IKEA スウェーデンカフェ とかもある
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
    "ホテルリブマックス",
    "ホテルルートイン",
    "ロイヤルパインズホテル",
    # その他ーーーーーーーーーー
    "カインズ",
    "キャンドゥ",
    ".*銀座惣菜店",
    ".*コーナン",
    "島忠",
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
        "かまどか": [
            "かまどか",
            "肉料理 和食 土鍋めし かまどか",
        ],
        "銀座ライオン": [
            "銀座ライオン",
            "ビアホール銀座ライオン",
        ],
        "京ほのか": [
            "京ほのか",
            "完全個室 居酒屋 京ほのか",
        ],
        "牛角": [
            "牛角",
            "炭火焼肉酒家 牛角",
            "炭火焼肉 牛角",
            "焼肉酒家 牛角",
        ],
        "木曽路": [
            "木曽路",
            "しゃぶしゃぶ 日本料理 木曽路",
        ],
        "九州じゃんがら": [
            "九州じゃんがら",
            "九州じゃんがららあめん",
        ],
        "くら寿司": [
            "くら寿司",
            "無添くら寿司",
        ],
        "五右衛門": [
            "五右衛門",
            "洋麺屋五右衛門",
        ],
        "CoCo壱番屋": [
            "CoCo壱番屋",
            "カレーハウスCoCo壱番屋",
        ],
        "コメダ珈琲店": [
            "コメダ珈琲店",
            "珈琲所 コメダ珈琲店",
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
        "新宿さぼてん": [
            "新宿さぼてん",
            "新宿とんかつ さぼてん",
            "新宿さぼてんデリカ",
            "とんかつ新宿さぼてん",
            "とんかつ新宿さぼてんデリカ",
        ],
        "四六時中": [
            "四六時中",
            "おひつごはん四六時中",
        ],
        "すたみな太郎NEXT": [
            "すたみな太郎NEXT",
            "食べ放題・バイキング すたみな太郎NEXT",
        ],
        "すた丼": [
            "元祖すた丼の店",
            "伝説のすた丼屋",
        ],
        "千年の宴": [
            "千年の宴",
            "個室空間 湯葉豆腐料理 千年の宴",
        ],
        "大吉": [
            "大吉",
            "やきとり大吉",
        ],
        "ダンダダン": [
            "ダンダダン酒場",
            "肉汁餃子のダンダダン",
        ],
        "ダンダダン酒場": [
            "ダンダダン酒場",
            "肉汁餃子製作所 ダンダダン酒場",
        ],
        "ちばチャン": [
            "ちばチャン",
            "大衆酒場 ちばチャン",
        ],
        "つぼ八": [
            "つぼ八",
            "北海道の恵み つぼ八",
        ],
        "ディプント": [
            "ワインの酒場 ディプント",
            "ワインの酒場。ディプント",
        ],
        "とんでん": [
            "和食レストランとんでん",
            "北海道生まれ和食処とんでん",
        ],
        "とりいちず": [
            "とりいちず",
            "水炊き・焼鳥・鶏餃子 とりいちず",
        ],
        "鳥貴族": [
            "鳥貴族",
            "焼鳥屋 鳥貴族",
        ],
        "土間土間": [
            "土間土間",
            "居酒屋 土間土間",
            "いつでも190円生ビール 創作居酒屋 土間土間",
        ],
        "馬車道": [
            "馬車道",
            "レストラン馬車道",
        ],
        "HUB": [
            "HUB",
            "BRITISH PUB HUB",
        ],
        "はなの舞": [
            "はなの舞",
            "海鮮居酒屋 はなの舞",
        ],
        "博多劇場": [
            "博多劇場",
            "屋台屋 博多劇場",
        ],
        "ブロンコビリー": [
            "ブロンコビリー",
            "ステーキハウス ブロンコビリー",
        ],
        "フレッシュネスバーガー": [
            "フレッシュネスバーガー",
            "FRESHNESS BURGER（フレッシュネスバーガー）",
        ],
        "北海道": [
            "北海道",
            "北の味紀行と地酒 北海道",
        ],
        "ポポラマーマ": [
            "ポポラマーマ",
            "ゆであげ生パスタ ポポラマーマ",
        ],
        "ミライザカ": [
            "ミライザカ",
            "旨唐揚げと居酒メシ ミライザカ",
        ],
        "山田うどん": [
            "山田うどん",
            "山田うどん食堂",
            "ファミリー食堂 山田うどん食堂",
        ],
        "酔っ手羽": [
            "酔っ手羽",
            "居酒屋革命酔っ手羽",
        ],
        "楽蔵": [
            "楽蔵",
            "全席個室 楽蔵",
        ],
        "リンガーハット": [
            "リンガーハット",
            "長崎ちゃんぽんリンガーハット",
        ],
        "和幸": [
            "和幸",
            "とんかつ和幸",
        ],
        "": [
            "",
            "",
        ],
    }

    chain_dict = {k: v for k, v in chain_dict.items() if k}  # 空除去
    store_name = store_name.replace(' ', '').replace('　', '')
    # chain_dict keyを回して該当するかチェック
    key = [s for s in chain_dict.keys() if s.replace(' ', '').replace('　', '') in store_name]
    if len(key) == 1:
        key = key[0]  # リスト解除
        kouho_list: list = chain_dict[key]
        kouho_list = [name.replace(' ', '').replace('　', '') for name in kouho_list]
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
