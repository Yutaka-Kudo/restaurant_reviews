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
    "おけがわマイン",
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
    ".*快活クラブ",
    "メディアカフェポパイ",
    "ゲラゲラ",
    # カラオケーーーーーーーーーー
    ".*歌うんだ村",
    ".*JOYSOUND",
    ".*ビッグエコー",
    ".*BIGECHO",
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
    ".*カラオケBanBan",
    ".*カラオケスタジオ",
    ".*カラオケステージ",
    ".*カラオケステーション",
    ".*カラオケセンター",
    ".*カラオケファンタジー",
    ".*カラオケラウンジ",
    ".*カラオケルーム",
    # 不動産ーーーーーーーーーーー
    ".*タウンハウジング",
    ".*株式会社エイブル",
    "ユウキホーム",
    ".*ピタットハウス",
    ".*ハウスコム",
    # コンビニーーーーーーーーーー
    "ファミリーマート",
    "ミスタードーナツ",
    "ニューヤマザキデイリーストア",
    "デイリーヤマザキ",
    "ローソン",
    "ナチュナルローソン",
    "ミニストップ",
    "セブンイレブン",
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
    "三井アウトレットパーク",
    # スーパーーーーーーーーーーー
    "イオン",
    "イオンモール",
    "カスミ",
    "カインズ",
    "キャンドゥ",
    ".*業務スーパー",
    # "IKEA", # IKEA スウェーデンカフェ とかもある
    "ダイエー",
    "ダイソー",
    "DAISO",
    ".*テンポス",
    "ベルク",
    "マックスバリュ",
    "マルエツ",
    "マミーマート",
    "無印良品",
    "ヤマダデンキ",
    "ヨークマート",
    "ワイズマート",
    # ホテルーーーーーーーーーー
    "アパホテル",
    "ホテルリブマックス",
    "ホテルルートイン",
    "アパマンショップ",
    "TOHOシネマズ",
    "スーパーホテル",
    "ロイヤルパインズホテル",
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


def chain_replace(store_name: str) -> list:

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
            "long": "海産物居酒屋 さくら水産"
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
        "コメダ珈琲店": {
            "short": "コメダ珈琲店",
            "long": "珈琲所 コメダ珈琲店"
        },
        "温野菜": {
            "short": "温野菜",
            "long": "しゃぶしゃぶ温野菜"
        },
        # "": {
        #     "short": "",
        #     "long": ""
        # },
        # "": {
        #     "short": "",
        #     "long": ""
        # },
        # "": {
        #     "short": "",
        #     "long": ""
        # },
    }

    import re
        # いきなりステーキ 松戸店
    chain_dict = {"いきなり": [
        "いきなり",
        "いきなり  ステーキ",
        "いきなり！ステーキ",
        "魁いきなりステーキ",
        ]}

    store_name = "いきなりステー  キ松戸市".replace(' ', '')
    # re.match("いきなり",store_name).group()

    store_name = store_name.replace(' ', '')
    # chain_dict keyを回して該当するかチェック
    key = [s for s in chain_dict.keys() if s.replace(' ', '') in store_name]
    if len(key) == 1:
        key = key[0]  # リスト解除
        kouho_list:list = chain_dict[key]
        kouho_list = [name.replace(' ', '') for name in kouho_list]
        try: 
            hit_sentence = max([re.match(s,store_name).group() for s in kouho_list if re.match(s,store_name)])
            kouho_list.remove(hit_sentence) # あるやつは除外してメモリ節約

            
            return [store_name.replace(hit_sentence,kouho) for kouho in kouho_list]

        except Exception:
            return []

        # key = key[0]  # リスト解除
        # if chain_dict[key]["long"].replace(' ', '') in store_name:  # 先に長い名前から当てはめる
        #     replaced_name = store_name.replace(chain_dict[key]["long"].replace(' ', ''), chain_dict[key]["short"].replace(' ', ''))
        # elif chain_dict[key]["short"].replace(' ', '') in store_name:
        #     replaced_name = store_name.replace(chain_dict[key]["short"].replace(' ', ''), chain_dict[key]["long"].replace(' ', ''))
        # else:
        #     replaced_name = ""
        # return replaced_name
    else:
        return []


def category_set(st_obj, category_list, errorlist=None):
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
        if errorlist:
            errorlist.append((type(e), e, category_list))


def name_set(st_obj: models.Store, store_name: str, mt_str: str, yomigana: str = "", yomi_roma: str = ""):
    
    if getattr(st_obj,f"store_name_{mt_str}") != store_name:
        st_obj.update_name(store_name, mt_str)

    if mt_str == "tb" and (yomigana or yomi_roma):  # 読み仮名をもっている自信のある食べログなら正式名称にする
        if getattr(st_obj,"store_name") != store_name:
            st_obj.update_name(store_name)

    # よみがなーーーーーーーーーーー
    if (yomigana and mt_str == "tb") or (yomigana and mt_str == "gn" and not st_obj.yomigana):
        if getattr(st_obj,"yomigana") != yomigana:
            st_obj.yomigana = yomigana
            st_obj.save()
    elif (mt_str == "google" and not st_obj.yomigana):
        kakasi = pykakasi.kakasi()
        conv = kakasi.convert(st_obj.store_name)
        st_obj.yomigana = "".join([s["hira"] for s in conv]).strip().replace(' ', '')[:99]
        st_obj.save()

    # よみローマーーーーーーーーーーーー
    if (yomi_roma and mt_str == "tb") or (yomi_roma and mt_str == "gn" and not st_obj.yomi_roma):
        if getattr(st_obj,"yomi_roma") != yomi_roma:
            st_obj.yomi_roma = yomi_roma
            st_obj.save()
    elif (mt_str == "google" and not st_obj.yomi_roma):
        kakasi = pykakasi.kakasi()
        conv = kakasi.convert(st_obj.store_name)
        st_obj.yomi_roma = "".join([s["hepburn"] for s in conv]).strip().replace(' ', '')[:99]
        st_obj.save()


def address_set(st_obj, address, mt_str):
    if (address and not st_obj.address) or (address and mt_str == "gn") or (address and mt_str == "tb"):
        if getattr(st_obj,"address") != address:
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
