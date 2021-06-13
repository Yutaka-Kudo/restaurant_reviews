import json
from googletrans import Translator
from janome.tokenizer import Tokenizer
import pykakasi


# import datetime
from devtools import debug
from pprint import pprint as pp

from scrape import models
from site_packages.my_module import store_model_process, atode_process

# st = models.Store.objects.get(store_name="ビアホフ 船橋FACE店")
# st.category
# gn,tb=models.Media_data.objects.filter(store__store_name="ビアホフ 船橋FACE店")
# models.Review.objects.filter(media=gn)
# models.Review.objects.filter(media=tb)


def insert_from_json(file, area1: str, area2: str, media_type: str):

    with open(file) as f:
        jfile = json.load(f)

    print(area1+" "+area2)

    media_type_obj = models.Media_type.objects.get(media_type=media_type)

    # area登録ーーーーーーーーーーーーー
    kakasi_hira = pykakasi.kakasi()
    kakasi_hira.setMode("J", "H")
    kakasi_hira.setMode("K", "H")
    converter_hira = kakasi_hira.getConverter()
    area_hira = converter_hira.do(area1+" "+area2)

    kakasi_roma = pykakasi.kakasi()
    kakasi_roma.setMode("H", "a")
    converter_roma = kakasi_roma.getConverter()
    area_roma = converter_roma.do(area_hira)

    area_obj, _ = models.Area.objects.update_or_create(
        area_name=area1+" "+area2,
        defaults={
            "yomigana": area_hira,
            "yomi_roma": area_roma,
        }
    )
    # ーーーーーーーーーーーーーーーー

    def create_ignoreList():
        area1_word = area1[:-1]
        area2_word = area2 if area1 == "東京都" else area2[:-1]
        ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
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

    for store_data in jfile:
        atode_dict = {}

        store_name = store_data["name"]

        # 電話ーーーーーーーーーーー
        try:
            phone = store_data["phone"]
        except Exception:
            phone = ""
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
        store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list, phone, category_list, yomigana, yomi_roma)

        atode_flg = _atode_flg
        atode_dict.update(_atode_dict)
        created_list += _created_list

        # media_data用ーーー
        url = store_data["url"]
        rate = store_data["rate"]
        review_count = store_data["review_count"]

        if atode_flg is False:
            media_obj, _ = models.Media_data.objects.update_or_create(
                store=store_obj, media_type=media_type_obj,
                defaults={
                    "url": url,
                    "rate": rate,
                    "review_count": review_count,
                }
            )
        else:
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

                    debug(date, content)

                    rev_obj, _ = models.Review.objects.update_or_create(
                        media=media_obj, content=content
                    )

                    if title:
                        rev_obj.title = title
                        rev_obj.save()
                    if date:
                        rev_obj.review_date = date
                        rev_obj.save()
                    if review_point:
                        rev_obj.review_point = review_point
                        rev_obj.save()
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

    print('作成は、')
    pp(created_list)

    # ーーーーーatode処理ーーーーーーーーーー
    # [{"store_name_db":a,"store_name_site":a,"phone":a,"url":a,"rate":a,
    # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
    #  {"name":a, ..........}]
    if atode_list:
        _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        created_list += _created_list

        print('作成は、')
        pp(created_list)
        print('不採用は、')
        pp(not_adopted_list)


# if __name__ == "__main__":
#     insert_from_json_tb()
