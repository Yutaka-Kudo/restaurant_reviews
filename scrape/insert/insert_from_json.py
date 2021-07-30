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
from site_packages.my_module import store_model_process, atode_process, setTotalRateForStore, make_rev_parts
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


def insert_from_json(file, area1: str, area2: str, mt_str: str):
    # 全角→半角 変換 googleが、、、
    ZEN = "".join(chr(0xff01 + i) for i in range(94))
    HAN = "".join(chr(0x21 + i) for i in range(94))
    ZEN2HAN = str.maketrans(ZEN, HAN)
    # HAN2ZEN = str.maketrans(HAN, ZEN)

    with open(file) as f:
        jfile = json.load(f)
    # jlen = len(jfile)
    # jfile = jfile[round(jlen / 2):]
    # jfile = jfile[200:]

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

        mt_obj: models.Media_type = models.Media_type.objects.get(media_type=mt_str)

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
        area_obj: models.Area
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
        # first_time = True if mt_str == "tb" else False
        # ーーーーーーーーーーーーーーーー

        def create_ignoreList():
            area2_for_ignore = area2[:-1] if area2[-1] == "市" else area2
            ignore_list = [
                ' ',
                '　',
                "店",
                "個室",
                "居酒屋",
                # area2_for_ignore,
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
        updated_name_list = []
        used_st_list = []

        # store処理ーーーーーーーーーーーーーー
        for enum, store_data in enumerate(jfile):
            print(f'\nあと {jfile_length-enum}')
            atode_dict = {}

            store_name = store_data["name"]
            print("----------------\n" + store_name)

            # 除外ネームならcontinue
            if store_name in IGNORE_STORE_NAME:
                print('除外ネーム')
                continue
            # 除外ネームならcontinue by_area
            if store_name in IGNORE_STORE_NAME_BY_AREA:
                print('除外ネーム')
                continue
            # 絶対飲食以外のワードならcontinue カラオケ等
            if [s for s in OTHER_THAN_RESTAURANTS if re.match(s.replace(' ', ''), store_name.replace(' ', ''))]:
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
                media_type=mt_str,
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
                continue

            atode_flg = _atode_flg
            atode_dict.update(_atode_dict)
            created_list += _created_list
            chain_list += _chain_list

            if atode_flg:
                # atode処理ーーーーーーーーーーーー
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

                atode_dict["collected"] = collected
                atode_dict["url"] = url
                atode_dict["rate"] = rate
                atode_dict["review_count"] = review_count

                # reviewーーーーーーーーーーーーーーー
                already_list = []
                atode_review_list = []

                # あとで消すーーーーーーー
                try:
                    store_data["review"]
                    rev_ok = True
                except KeyError:
                    rev_ok = False
                if rev_ok:
                # あとで消すーーーーーーー

                    for rev in store_data["review"]:

                        if rev["content"] in already_list:
                            continue

                        title, content, date, log_num, review_point = make_rev_parts(rev)

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

                atode_dict["review"] = atode_review_list
                atode_list.append(atode_dict)
                # ーーーーーーーーーーーーatode処理end

            else:
                used_st_list.append(store_obj)

                if origin_name:
                    updated_name_list.append(origin_name)
        # ーーーーーーーーーーーーーー store処理end

        # models.Store.objects.filter(store_name="こまや")[0].pk
        # models.Media_data.objects.filter(store__store_name="こまや")[1].media_type.id

        # media_data処理ーーーーーーーーーーーーーーー
        exist_md_objs = models.Media_data.objects.select_related("store").filter(store__in=used_st_list, media_type=mt_obj)
        bulk_update_md_list = []
        bulk_create_md_list = []
        bulk_delete_list = []
        bulk_review_list = []
        jfile_length = len(jfile)
        for enum, store_data in enumerate(jfile):
            print(f'\nあと {jfile_length - enum}')
            print(f'name: {store_data["name"]}')

            searched_mds = [md for md in exist_md_objs if getattr(md.store, f"store_name_{mt_str}") == store_data["name"]]

            if len(searched_mds) >= 2:  # エラーパターン 重複店名
                print(f'エラーリスト追加 同store_name_{mt_str} {store_data["name"]}')
                print([md.store.store_name for md in searched_mds])
                raise Exception()

            # media_data用ーーー
            url = store_data["url"][:1000]
            try:
                collected = store_data["collected"]
            except Exception:
                collected = None
            try:
                rate = store_data["rate"]
            except Exception:
                rate = 0
            try:
                review_count = store_data["review_count"]
            except Exception:
                review_count = 0

            if searched_mds:
                md_obj: models.Media_data = searched_mds[0]

                md_obj.collected = collected
                md_obj.url = url
                md_obj.rate = rate
                md_obj.review_count = review_count
                bulk_update_md_list.append(md_obj)
                print('set md to bulk_update_list')

                # review削除用idリスト
                rev_objs = models.Review.objects.filter(media=md_obj).only("pk")
                bulk_delete_list += [r.pk for r in rev_objs]
            else:
                try:
                    st_obj = next((st for st in used_st_list if getattr(st, "store_name") == store_data["origin_name"]), None)
                except KeyError:
                    st_obj = next((st for st in used_st_list if getattr(st, f"store_name_{mt_str}") == store_data["name"]), None)
                if st_obj:
                    md_obj = models.Media_data(
                        store=st_obj,
                        media_type=mt_obj,
                        collected=collected,
                        url=url,
                        rate=rate,
                        review_count=review_count,
                    )
                    bulk_create_md_list.append(md_obj)
                    print('set md to bulk_create_list')

        if bulk_update_md_list:
            models.Media_data.objects.bulk_update(bulk_update_md_list, ["collected", "url", "rate", "review_count"])
            print('bulk_update_md_list')

        # 確認用
        import collections
        if mt_str == "google":
            counter = collections.Counter([getattr(s.store, "store_name") for s in bulk_create_md_list])
        else:
            counter = collections.Counter([getattr(s.store, f"store_name_{mt_str}") for s in bulk_create_md_list])
        dupli_create_md = [s for s in counter if counter[s] >= 2]  # 出現回数2以上
        debug(dupli_create_md)
        # 確認用

        if bulk_create_md_list:
            models.Media_data.objects.bulk_create(bulk_create_md_list)
            print('bulk_create_md_list')
        # ーーーーーーーーーーーーーーーmedia_data処理end

        # review処理ーーーーーーーーーーー
        md_objs_after_create = models.Media_data.objects.select_related("store").filter(store__in=used_st_list, media_type=mt_obj)
        for enum, store_data in enumerate(jfile):
            print(f'\nあと {jfile_length - enum}')
            md_obj = next((md for md in md_objs_after_create if getattr(md.store, f"store_name_{mt_str}") == store_data["name"]), None)
            if md_obj:
                print(f'name: {store_data["name"]}')

                # あとで消すーーーーーーー
                try:
                    store_data["review"]
                except KeyError:
                    continue
                # あとで消すーーーーーーー

                try:
                    already_list = []

                    for rev in store_data["review"]:

                        if rev["content"] in already_list:
                            continue

                        title, content, date, log_num, review_point = make_rev_parts(rev)
                        print(date, content[:20])

                        new_rev_obj = models.Review(
                            media=md_obj,
                            title=title,
                            content=content,
                            review_date=date,
                            review_point=review_point,
                            log_num_byTabelog=log_num
                        )

                        bulk_review_list.append(new_rev_obj)
                        already_list.append(rev["content"])

                    print('レビュー確認!!bulk_review_list.append')

                except KeyError:
                    print('no 口コミ')
        # ーーーーーーーーーーーreview処理end

        if bulk_delete_list:
            models.Review.objects.filter(pk__in=bulk_delete_list).delete()
            print('bulk削除 レビュー')
        if bulk_review_list:
            models.Review.objects.bulk_create(bulk_review_list)
            print('bulkクリエイト レビュー')
        # ーーーーーーーーーーーreview処理 リアルにend

        # 店ごとのtotal_rate登録ーーーーー
        st_obj_len = len(used_st_list)
        for enum, st in enumerate(used_st_list):
            print(f'total_rate登録 あと {st_obj_len-enum} 店')
            st: models.Store
            store_md = models.Media_data.objects.filter(store=st)
            total_rate = setTotalRateForStore(store_md)
            st.total_rate = total_rate
            st.save()

            # 店ごとのtotal_review_count登録ーーーーー
            rev_cnt_list = [md.review_count for md in store_md if md.review_count]
            try:
                total_review_count = sum(rev_cnt_list)
            except ZeroDivisionError:
                total_review_count = 0
            st.total_review_count = total_review_count
            st.save()

        print('作成は、')
        pp(created_list)
        print('チェーンリスト')
        print(chain_list)

        # ーーーーーatode処理ーーーーーーーーーー
        # [{"store_name_db":a,"store_name_site":a,"phone":a,"url":a,"rate":a,
        # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
        #  {"name":a, ..........}]
        if atode_list:
            filename = os.path.basename(file)
            subprocess.run(['noti', "-t", "next.あとでプロセス", "-m", f"{filename}"])
            _created_list, not_adopted_list, doubt_list, closed_list = atode_process(atode_list, mt_obj, area_obj, updated_name_list)

            created_list += _created_list

            print('作成は、')
            pp(created_list)
            print('不採用は、')
            pp(not_adopted_list)

            if doubt_list:
                import datetime
                # n = datetime.datetime.now() + datetime.timedelta(hours=9)
                n = datetime.datetime.now()
                with open(f"/Users/yutakakudo/Google ドライブ/colab/json/doubt_{mt_str}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
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
