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
from site_packages.my_module import store_model_process, atode_process
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

    try:
        with open(file) as f:
            jfile = json.load(f)

        # jfile = jfile[-79:]

        print(area1 + " " + area2)

        media_type_obj = models.Media_type.objects.get(media_type=media_type)

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
        # ーーーーーーーーーーーーーーーー

        def create_ignoreList():
            # area1_word = area1[:-1]
            # area2_word = area2 if area1 == "東京都" else area2[:-1]
            # ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
            ignore_list = [' ', "店", "個室", "居酒屋"]
            # ignore_listに英語も入れる
            tr = Translator()
            # del ignore_list[0] # 最初に入ってる空白を消す
            add_ignore = []
            for src in ignore_list[1:]:
                try:
                    en_word = tr.translate(src, src='ja', dest='en').text.lower()
                    add_ignore.append(en_word)
                except Exception as e:
                    print(type(e), e)
            ignore_list += add_ignore
            ignore_list.append("store")
            return ignore_list
        ignore_list = create_ignoreList()

        atode_list = []
        created_list = []
        chain_list = []
        jfile_length = len(jfile)

        for store_data in jfile:
            print(f'あと {jfile_length}')
            atode_dict = {}

            store_name = store_data["name"]
            print("----------------\n" + store_name)

            # 除外ネームならcontinue
            if store_name in IGNORE_STORE_NAME:
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
                first_time=first_time
            )

            atode_flg = _atode_flg
            atode_dict.update(_atode_dict)
            created_list += _created_list
            chain_list += _chain_list

            # media_data用ーーー
            try:
                collected = store_data["collected"]
            except Exception:
                collected = None

            url = store_data["url"]

            try:
                rate = store_data["rate"]
            except Exception:
                rate = 0

            try:
                review_count = store_data["review_count"]
            except Exception:
                review_count = 0

            if not atode_flg:
                media_obj, _ = models.Media_data.objects.update_or_create(
                    store=store_obj, media_type=media_type_obj,
                    defaults={
                        "collected": collected,
                        "url": url,
                        "rate": rate,
                        "review_count": review_count,
                    }
                )

                all_md = models.Media_data.objects.filter(store=store_obj)

                # 店ごとのtotal_rate登録ーーーーー
                rate_md = [md for md in all_md if md.media_type.__str__() in ["gn", "google", "tb", "uber"]]
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
                store_obj.total_rate = total_rate
                store_obj.save()

                # 店ごとのtotal_review_count登録ーーーーー
                rev_cnt_list = [md.review_count for md in all_md if md.review_count]
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

            try:
                atode_review_list = []
                for i, rev in enumerate(store_data["review"]):

                    try:
                        title = rev["title"]
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

                        if i == 0:  # 初期ループ時にデータ消して刷新
                            models.Review.objects.filter(media=media_obj).delete()
                            print('ReviewObj delete for renewal')

                        print(date, content[:20])

                        rev_obj, _ = models.Review.objects.update_or_create(
                            media=media_obj, content=content
                        )

                        if title:
                            # 長さ制限
                            if len(title) > 100:
                                title = title[:100]
                            rev_obj.title = title
                        if date:
                            rev_obj.review_date = date
                        if review_point:
                            rev_obj.review_point = review_point
                        if log_num:
                            rev_obj.log_num_byTabelog = log_num

                        rev_obj.save()

                        print('レビュー登録!!')
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
            # subprocess.run(["say", "選びなさい"])
            subprocess.run(['noti', "-t", "next.あとでプロセス", "-m", f"{filename}"])
            _created_list, not_adopted_list, doubt_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

            created_list += _created_list

            print('作成は、')
            pp(created_list)
            print('不採用は、')
            pp(not_adopted_list)

            if doubt_list:
                print('疑わしきは、 ')
                pp(doubt_list)

                import datetime
                # n = datetime.datetime.now() + datetime.timedelta(hours=9)
                n = datetime.datetime.now()
                with open(f"/Users/yutakakudo/Google ドライブ/colab/json/doubt_{media_type}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
                    for i, line in enumerate(doubt_list):
                        f.write(f"{line}\n")
                        if i % 2 == 1:
                            f.write("\n")

        # エリア別登録数、登録------------
        area_obj.registed = len(models.Store.objects.filter(area=area_obj))
        area_obj.save()

    except Exception as e:
        subprocess.run(['noti', "-m", "エラー"])
        raise Exception(type(e), e)

# if __name__ == "__main__":
#     insert_from_json_tb()
