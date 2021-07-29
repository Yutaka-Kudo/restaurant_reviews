import json
import re
import os
from devtools import debug
from pprint import pprint as pp
import subprocess
from decimal import Decimal

from googletrans import Translator
import pykakasi


from scrape import models
from site_packages.my_module import store_model_process, atode_process, setTotalRateForStore
from site_packages.sub import IGNORE_STORE_NAME, OTHER_THAN_RESTAURANTS

# st = models.Store.objects.get(store_name="ビアホフ 船橋FACE店")
# st.category
# gn,tb=models.Media_data.objects.filter(store__store_name="ビアホフ 船橋FACE店")
# models.Review.objects.filter(media=gn)
# models.Review.objects.filter(media=tb)
# with open("/users/yutakakudo/downloads/gn_千葉県_船橋市_2021-06-13_1857.json") as f:
#     jfile = json.load(f)
# for i in jfile:
#     print(i["name"])
# models.Area_major.objects.all()


def insert_from_json(file, area1: str, area2: str, media_type: str):
    # 全角→半角 変換 googleが、、、
    ZEN = "".join(chr(0xff01 + i) for i in range(94))
    HAN = "".join(chr(0x21 + i) for i in range(94))
    ZEN2HAN = str.maketrans(ZEN, HAN)
    # HAN2ZEN = str.maketrans(HAN, ZEN)

    with open(file) as f:
        jfile = json.load(f)
    # jlen = len(jfile)
    # jfile = jfile[round(jlen / 2):]
    # jfile = jfile[85:89]

    # エリア別ignore_list
    try:  # あったら読み込む
        with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/IGNORENAME_{area1}_{area2}.txt") as f:
            IGNORE_STORE_NAME_BY_AREA = [s.strip() for s in f.readlines()]
    except Exception:  # なければ作っとく
        with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/IGNORENAME_{area1}_{area2}.txt", "x") as f:
            # f.write("")
            pass
        IGNORE_STORE_NAME_BY_AREA = []

    try:
        print(area1 + " " + area2)

        media_type_obj:models.Media_type = models.Media_type.objects.get(media_type=media_type)

        # area登録ーーーーーーーーーーーーー
        kakasi = pykakasi.kakasi()

        # 県名 area_major
        area_m_hira = "".join([s["hira"] for s in kakasi.convert(area1)])
        area_m_roma = "".join([s["hepburn"] for s in kakasi.convert(area1)])
        area_m_obj, _ = models.Area_major.objects.update_or_create(
            area_name=area1,
            defaults={
                "yomigana": area_m_hira,
                "yomi_roma": area_m_roma,
            }
        )

        # 県・市
        area_name = area1 + " " + area2

        area_obj:models.Area
        area_hira = "".join([s["hira"] for s in kakasi.convert(area_name)])
        area_roma = "".join([s["hepburn"] for s in kakasi.convert(area_hira)])
        area_obj, _created = models.Area.objects.update_or_create(
            area_name=area_name,
            defaults={
                "major_area": area_m_obj,
                "yomigana": area_hira,
                "yomi_roma": area_roma,
            }
        )
        # 初めてフラグ
        first_time = True if _created else False
        # first_time = True if media_type == "tb" else False
        # ーーーーーーーーーーーーーーーー

        def create_ignoreList():
            area2_for_ignore = area2[:-1] if area2[-1] == "市" else area2
            ignore_list = [
                ' ',
                '　',
                "店",
                "個室",
                "居酒屋",
                area2_for_ignore,
                # 料理
                # "焼鳥",
                # "焼き鳥",
                # "焼とり",
                # "焼きとり",
                # "やきとり",
                "焼",
                "焼き",
                # "蕎麦",
                # "そば",
                # "ラーメン",
                # "らーめん",
                # "拉麺",
                # "中華",
                # "カレー",
                # "串カツ",
                # "串かつ",
                # "焼肉",
                # "焼き肉",
                # "やき肉",
                # "やきにく",
                "唐揚",
                "唐揚げ",
                "から揚げ",
                "からあげ",
                # "寿司",
                # "鮨",
                # "寿し",
                # "すし",
                # "しゃぶしゃぶ",
                # "串焼",
                # "串焼き",
                # "とんかつ",
                "",
                "",
                "",
                "",
                "",
                "",
                # 業態、特徴
                # "レストラン",
                # "ダイニング",
                # "カフェ",
                # "バー", # 「bar 豊」と「豊鮨」で重複しちゃう
                "炭火",
                "立ち飲み",
                "立ち呑み",
                "",
                "",
                "",
                "",
                "",
                # 国
                "スペイン",
                "イタリアン",
                "フランス",
                "",
                "",
                "",
                "",
            ]
            ignore_list = [s for s in ignore_list if s]  # 空削除
            # ignore_listに英語も入れる
            tr = Translator()
            add_ignore = []
            for src in ignore_list[2:]:
                try:
                    en_word = tr.translate(src, src='ja', dest='en').text.lower()
                    add_ignore.append(en_word)
                except Exception as e:
                    print(type(e), e)
            ignore_list += add_ignore
            ignore_list.append("store")
            print(ignore_list)
            return ignore_list
        ignore_list = create_ignoreList()

        atode_list = []
        created_list = []
        chain_list = []
        jfile_length = len(jfile)
        # bulk_md_list = []
        bulk_delete_list = []
        bulk_review_list = []
        updated_name_list = []
        
        for store_data in jfile:
            print(f'\nあと {jfile_length}')
            atode_dict = {}

            store_name = store_data["name"]
            print("----------------\n" + store_name)

            # 除外ネームならcontinue
            if store_name in IGNORE_STORE_NAME:
                jfile_length -= 1
                print('除外ネーム')
                continue
            # 除外ネームならcontinue by_area
            if store_name in IGNORE_STORE_NAME_BY_AREA:
                jfile_length -= 1
                print('除外ネーム')
                continue
            # 絶対飲食以外のワードならcontinue カラオケ等
            if [s for s in OTHER_THAN_RESTAURANTS if re.match(s.replace(' ', ''), store_name.replace(' ', ''))]:
                jfile_length -= 1
                print('飲食以外ネーム')
                continue

            # 電話ーーーーーーーーーーー
            try:
                phone = store_data["phone"]
            except Exception:
                phone = ""
            # ーーーーーーーーーーーーー

            # 住所ーーーーーーーーーーー
            try:
                address = store_data["address"]
                # 全角→半角 変換 googleが、、、
                address = address.translate(ZEN2HAN)
                address = address.replace('日本、', '').strip()
            except Exception:
                address = ""
            # ーーーーーーーーーーーーー

            # 食べログのジャンルーーーーー
            try:
                category_list = store_data["category"]
            except Exception:
                category_list = None
            # ーーーーーーーーーーーーーー

            # 読み仮名ーーーーーーーーーー
            try:
                yomigana = store_data["yomigana"]
            except Exception:
                yomigana = ""

            try:
                yomi_roma = store_data["yomi_roma"]
            except Exception:
                yomi_roma = ""
            # ーーーーーーーーーーーー

            # refill用ーーーーーーーー
            try:
                origin_name = store_data["origin_name"]
            except Exception:
                origin_name = ""

            # 店名でstore_object取得  1番近いものを探すーーーー
            store_obj, _atode_flg, _atode_dict, _created_list, _chain_list = store_model_process(
                area_obj=area_obj,
                media_type=media_type,
                store_name=store_name,
                ignore_list=ignore_list,
                phone=phone,
                address=address,
                category_list=category_list,
                yomigana=yomigana,
                yomi_roma=yomi_roma,
                first_time=first_time,
                origin_name=origin_name,
            )

            if not store_obj:
                print('店名消しちゃったor変えちゃった')
                jfile_length -= 1
                continue

            atode_flg = _atode_flg
            atode_dict.update(_atode_dict)
            created_list += _created_list
            chain_list += _chain_list

            # media_data用ーーー
            try:
                collected = store_data["collected"]
            except Exception:
                collected = None

            url = store_data["url"][:1000]

            try:
                rate = store_data["rate"]
            except Exception:
                rate = 0

            try:
                review_count = store_data["review_count"]
            except Exception:
                review_count = 0

            if not atode_flg:

                if origin_name:
                    updated_name_list.append(origin_name)

                md_obj:models.Media_data
                md_obj.store = store_obj
                md_obj.media_type = media_type_obj
                md_obj.collected = collected
                md_obj.url = url
                md_obj.rate = rate
                md_obj.review_count = review_count
                bulk_md_list.append(md_obj)

                md_obj, _ = models.Media_data.objects.update_or_create(
                    store=store_obj, media_type=media_type_obj,
                    defaults={
                        "collected": collected,
                        "url": url,
                        "rate": rate,
                        "review_count": review_count,
                    }
                )

                store_md = models.Media_data.objects.filter(store=store_obj)
                # 店ごとのtotal_rate登録ーーーーー
                total_rate = setTotalRateForStore(store_md)
                store_obj.total_rate = total_rate
                store_obj.save()

                # 店ごとのtotal_review_count登録ーーーーー
                rev_cnt_list = [md.review_count for md in store_md if md.review_count]
                try:
                    total_review_count = sum(rev_cnt_list)
                except ZeroDivisionError:
                    total_review_count = 0
                store_obj.total_review_count = total_review_count
                store_obj.save()

            else:
                atode_dict["collected"] = collected
                atode_dict["url"] = url
                atode_dict["rate"] = rate
                atode_dict["review_count"] = review_count

            # 口コミーーーーーーーーーー
            if atode_flg is False:
                # データ消して刷新
                rev_objs = models.Review.objects.filter(media=md_obj).only("pk")
                bulk_delete_list += [r.pk for r in rev_objs]
                print('ReviewObj delete for renewal')

            try:
                already_list = []
                atode_review_list = []
                for rev in store_data["review"]:

                    if rev["content"] in already_list:
                        continue

                    try:
                        title = rev["title"][:100]  # 長さ制限
                    except KeyError:
                        title = None
                    try:
                        content = rev["content"]
                    except KeyError:
                        content = None
                    try:
                        date = rev["date"]
                    except KeyError:
                        date = None
                    try:
                        log_num = rev["log_num"]
                    except KeyError:
                        log_num = None
                    try:
                        review_point = rev["review_point"]
                    except KeyError:
                        review_point = None

                    if atode_flg is False:

                        print(date, content[:20])

                        new_rev_obj = models.Review(
                            title=title,
                            content=content,
                            media=md_obj,
                            review_date=date,
                            review_point=review_point,
                            log_num_byTabelog=log_num
                        )
                        bulk_review_list.append(new_rev_obj)

                        print('レビュー確認!!')
                    else:
                        # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                        # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                        atode_review_dict = {}
                        atode_review_dict["title"] = title
                        atode_review_dict["content"] = content
                        atode_review_dict["date"] = date
                        atode_review_dict["log_num"] = log_num
                        atode_review_dict["review_point"] = review_point
                        atode_review_list.append(atode_review_dict)

                    already_list.append(rev["content"])

                # atode処理ーーーーーーーーー
                if atode_flg:
                    atode_dict["review"] = atode_review_list
                # ーーーーーーーーーーーー
            except KeyError:
                print('no 口コミ')
                atode_dict["review"] = []
            if atode_flg:
                atode_list.append(atode_dict)

            jfile_length -= 1

        models.Review.objects.filter(pk__in=bulk_delete_list).delete()
        print('bulk削除 レビュー')
        models.Review.objects.bulk_create(bulk_review_list)
        print('bulkクリエイト レビュー')

        print('作成は、')
        pp(created_list)

        print('チェーンリスト')
        print(chain_list)

        filename = os.path.basename(file)

        # ーーーーーatode処理ーーーーーーーーーー
        # [{"store_name_db":a,"store_name_site":a,"phone":a,"url":a,"rate":a,
        # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
        #  {"name":a, ..........}]
        if atode_list:
            subprocess.run(['noti', "-t", "next.あとでプロセス", "-m", f"{filename}"])
            _created_list, not_adopted_list, doubt_list, closed_list = atode_process(atode_list, media_type_obj, area_obj, updated_name_list)

            created_list += _created_list

            print('作成は、')
            pp(created_list)
            print('不採用は、')
            pp(not_adopted_list)

            if doubt_list:
                import datetime
                # n = datetime.datetime.now() + datetime.timedelta(hours=9)
                n = datetime.datetime.now()
                with open(f"/Users/yutakakudo/Google ドライブ/colab/json/doubt_{media_type}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
                    for line in doubt_list:
                        f.write(f"{line}\n")
                        if "DBの名前" in line or "生還" in line:
                            f.write("\n")
                print('doubt_list作成！')
            if closed_list:
                # 既存のファイルの末尾が改行になってるか
                try:
                    with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/IGNORENAME_{area1}_{area2}.txt", "r") as f:
                        reads = f.read()[-1]
                except Exception:
                    reads = "\n"
                with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/IGNORENAME_{area1}_{area2}.txt", "a") as f:
                    if reads == "\n":
                        f.write("\n".join(closed_list))
                    else:
                        f.write("\n")
                        f.write("\n".join(closed_list))
                print('closed_list作成')

        # エリア別登録数、登録------------
        area_obj.registed = len(models.Store.objects.filter(area=area_obj))
        area_obj.save()

    except Exception as e:
        subprocess.run(['noti', "-m", "エラー"])
        raise Exception(type(e), e)

# if __name__ == "__main__":
#     insert_from_json_tb()
