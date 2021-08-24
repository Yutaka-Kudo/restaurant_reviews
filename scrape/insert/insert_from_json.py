import json
import re
import os
from devtools import debug
from pprint import pprint as pp
import subprocess
from decimal import Decimal

from googletrans import Translator
import pykakasi
import datetime
import collections
import datetime


from scrape import models
from site_packages import my_module
# from site_packages.my_module import my_module.make_rev_parts
from site_packages import sub
from scrape.scrape_kit import duplicated_by_google_memo

import importlib


def insert_from_json(file_list, area1: str, area2: str, mt_str: str, doubt_list: list = None, names_for_second_attack: list = None, store_objs=None, is_atode_file: str = "", created_list: list = None):
    importlib.reload(my_module)
    importlib.reload(sub)
    print("モジュールリロード my_module")

    atode_list = []
    if created_list is None:
        created_list = []
    chain_list = []
    # bulk_md_list = []
    updated_name_list = []
    used_st_list = []
    errorlist = []
    mt_obj: models.Media_type = models.Media_type.objects.get(media_type=mt_str)

    jfile = []
    for file in file_list:
        with open(file) as f:
            file_one = json.load(f)
        jfile += file_one
    jlen = len(jfile)
    # jfile = jfile[:round(jlen / 2)]
    # jfile = jfile[200:]

    if is_atode_file:
        area_obj = models.Area.objects.get(area_name=area1 + " " + area2)
        dupli_names = []
        atode_list = jfile
    else:
        if doubt_list is None:
            doubt_list = []

        # 全角→半角 変換 googleが、、、
        ZEN = "".join(chr(0xff01 + i) for i in range(94))
        HAN = "".join(chr(0x21 + i) for i in range(94))
        ZEN2HAN = str.maketrans(ZEN, HAN)
        # HAN2ZEN = str.maketrans(HAN, ZEN)

        if not mt_str == "google":
            # colletedの違いのみの重複は統一
            counter = collections.Counter([n["name"] for n in jfile])
            dupli_store_list = [s for s in counter if counter[s] >= 2]  # 出現回数2以上
            for d_store in dupli_store_list:
                sts = [store for store in jfile if store["name"] == d_store]
                latest_collected: str = max([datetime.datetime.strptime(store["collected"], "%Y-%m-%d").date() for store in sts]).strftime("%Y-%m-%d")
                for filedata in jfile:
                    if filedata["name"] == d_store:
                        filedata["collected"] = latest_collected

                # reviewのlog_numをmaxに統一。短時間でもlog_numが上がることがある
                contents = []
                for store in sts:
                    if store.get("review"):
                        contents += [rev["content"] for rev in store["review"]]
                unique_contents = list(set(contents))
                for u_content in unique_contents:
                    log_num_list = []
                    for store in sts:
                        if store.get("review"):
                            for rev in store["review"]:
                                if rev["content"] == u_content and rev.get("log_num"):
                                    log_num_list.append(int(rev["log_num"]))
                    if log_num_list:
                        max_log_num = max(log_num_list)
                        for filedata in jfile:
                            if filedata.get('review'):
                                for rev in filedata["review"]:
                                    if rev["content"] == u_content:
                                        rev["log_num"] = max_log_num

            # 重複削除
            jfile = list(map(json.loads, set(map(json.dumps, jfile))))

            # もしプロパティの違い(データ取得日以外)で重複削除できなければ
            counter = collections.Counter([n["name"] for n in jfile])
            dupli_store_list = [s for s in counter if counter[s] >= 2]  # 出現回数2以上
            if dupli_store_list:
                print('重複した店舗があります jsonファイルを直接修正してください')
                print(dupli_store_list)
                raise Exception()
        else:
            # 重複削除
            jfile = list(map(json.loads, set(map(json.dumps, jfile))))

            # もしプロパティの違い(データ取得日以外)で重複削除できなければ ← googleはやってない
            counter = collections.Counter([n["origin_name"] for n in jfile])
            dupli_store_list = [s for s in counter if counter[s] >= 2]  # 出現回数2以上
            if dupli_store_list:
                print('重複した店舗があります jsonファイルを直接修正してください')
                print(dupli_store_list)
                raise Exception()

        # 2撃目以降
        if names_for_second_attack:
            name_site_list = [n["store_name_site"] for n in names_for_second_attack]
            jfile = [j for j in jfile if j["name"] in name_site_list]

        # エリア別ignore_list
        try:  # あったら読み込む
            with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt") as f:
                IGNORE_STORE_NAME_BY_AREA = [s.strip() for s in f.readlines()]
        except Exception:  # なければ作っとく
            with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "x") as f:
                # f.write("")
                pass
            IGNORE_STORE_NAME_BY_AREA = []

        print(area1 + " " + area2)

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

        if not store_objs:  # 持ち越しstore_objsなければ
            store_objs = models.Store.objects.filter(area=area_obj)
            # store_objs = models.Store.objects.filter(area__area_name="東京都 浅草駅")
            # len(store_objs)

        jfile_length = len(jfile)
        # store処理ーーーーーーーーーーーーーー
        bulk_st_list = []
        for enum, file_data in enumerate(jfile):
            print(f'\nあと {jfile_length-enum}')
            atode_dict = {}

            store_name: str = file_data["name"][:100]
            print("----------------\n" + store_name)

            # refill用ーーーーーーーー
            try:
                origin_name = file_data["origin_name"]
            except Exception:
                origin_name = ""

            if origin_name:
                print(f'origin: {origin_name}')
                store_objs = models.Store.objects.filter(area=area_obj, store_name=origin_name)
                if not store_objs:
                    print('店名消しちゃったor変えちゃった')
                    continue
            # ーーーーーーーーーーーー

            if not origin_name:
                # 除外ネームならcontinue
                if store_name in sub.IGNORE_STORE_NAME:
                    print('除外ネーム')
                    continue
                # 除外ネームならcontinue by_area
                if store_name in IGNORE_STORE_NAME_BY_AREA:
                    print('除外ネーム')
                    continue
                # 飲食以外のワードならcontinue カラオケ等
                if [s for s in sub.OTHER_THAN_RESTAURANTS if re.match(s.replace(' ', '').replace('　', ''), store_name.replace(' ', '').replace('　', ''))]:
                    print('飲食以外ネーム')
                    continue

            # 電話ーーーーーーーーーーー
            try:
                phone = file_data["phone"]
            except Exception:
                phone = ""
            # ーーーーーーーーーーーーー

            # 住所ーーーーーーーーーーー
            try:
                address = file_data["address"]
                # 全角→半角 変換 googleが、、、
                address = address.translate(ZEN2HAN)
                address = address.replace('日本、', '').replace('丁目', '-').strip()
            except Exception:
                address = ""
            # ーーーーーーーーーーーーー

            # 食べログのジャンルーーーーー
            try:
                category_list = file_data["category"]
            except Exception:
                category_list = []
            # ーーーーーーーーーーーーーー

            # 読み仮名ーーーーーーーーーー
            try:
                yomigana = file_data["yomigana"]
            except Exception:
                yomigana = ""

            try:
                yomi_roma = file_data["yomi_roma"]
            except Exception:
                yomi_roma = ""
            # ーーーーーーーーーーーー

            # 初期登録時ーーーー
            if first_time:
                try:
                    category1 = category_list[0]
                except Exception:
                    category1 = None
                try:
                    category2 = category_list[1]
                except Exception:
                    category2 = None
                try:
                    category3 = category_list[2]
                except Exception:
                    category3 = None
                st = models.Store(
                    area=area_obj,
                    store_name=store_name,
                    yomigana=yomigana,
                    yomi_roma=yomi_roma,
                    phone_number=phone,
                    address=address,
                    category1=category1,
                    category2=category2,
                    category3=category3,
                )
                setattr(st, f"store_name_{mt_str}", store_name)
                bulk_st_list.append(st)
                continue
            # ーーーー初期登録時

            # 店名でstore_object取得  1番近いものを探すーーーー
            store_obj, _atode_flg, _atode_dict, _created_list, _chain_list = my_module.store_model_process(
                store_objs=store_objs,
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

            atode_flg = _atode_flg
            atode_dict.update(_atode_dict)
            created_list += _created_list
            chain_list += _chain_list

            if atode_flg:
                # atode処理ーーーーーーーーーーーー
                # media_data用ーーー
                try:
                    collected = file_data["collected"]
                except Exception:
                    collected = None

                url = file_data["url"][:1000]

                try:
                    rate = file_data["rate"]
                except Exception:
                    rate = 0

                try:
                    review_count = file_data["review_count"]
                except Exception:
                    review_count = 0

                atode_dict["collected"] = collected
                atode_dict["url"] = url
                atode_dict["rate"] = rate
                atode_dict["review_count"] = review_count

                # reviewーーーーーーーーーーーーーーー
                already_rev_list = []
                atode_review_list = []

                try:
                    file_data["review"]
                except KeyError:
                    pass
                else:
                    for rev in file_data["review"]:

                        if rev["content"] in already_rev_list:
                            continue

                        title, content, date, log_num, review_point = my_module.make_rev_parts(rev)

                        # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                        # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                        atode_review_dict = {}
                        atode_review_dict["title"] = title
                        atode_review_dict["content"] = content
                        atode_review_dict["date"] = date
                        atode_review_dict["log_num"] = log_num
                        atode_review_dict["review_point"] = review_point
                        atode_review_list.append(atode_review_dict)

                        already_rev_list.append(rev["content"])

                atode_dict["review"] = atode_review_list
                atode_list.append(atode_dict)
                # ーーーーーーーーーーーーatode処理end

            else:
                # かぶった場合に例外ーーーーーー
                if store_obj in used_st_list:
                    print('\n店舗が重複しています。')
                    print(f'this name : {store_name}')
                    print(f'name in db: {store_obj.store_name}')
                    raise Exception()
                # ーーーーーーーーーーーーーーーー

                used_st_list.append(store_obj)

                # 使ったものはその後比較に持ち出さない
                store_objs = store_objs.exclude(pk=store_obj.pk)  # ないPKでもエラーにならない

                if origin_name:
                    updated_name_list.append(origin_name)
                else:
                    updated_name_list.append(store_name)

            print(f'store_objsカウント {store_objs.count()}')

        # 初期登録時、一括！
        if bulk_st_list:
            models.Store.objects.bulk_create(bulk_st_list)
            print('bulk_create_store_list')
            used_st_list = models.Store.objects.filter(area=area_obj)
        # ーーーーーーーーーーーーーー store処理end

        # media_data処理ーーーーーーーーーーーーーーー
        exist_md_objs = models.Media_data.objects.select_related("store").filter(store__in=used_st_list, media_type=mt_obj)
        bulk_update_md_list = []
        bulk_create_md_list = []
        bulk_delete_list = []
        bulk_review_list = []
        dupli_names = []
        jfile_length = len(jfile)
        inspection_dict: dict[str, int] = {}

        # jfileをused_st_listで絞る
        if jfile[0].get("origin_name"):
            jfile = [s for s in jfile if s["origin_name"] in updated_name_list]
        else:
            jfile = [s for s in jfile if s["name"] in updated_name_list]
        jfile_length = len(jfile)

        for enum, file_data in enumerate(jfile):
            file_data["name"] = file_data["name"][:100]
            print(f'\nあと {jfile_length - enum}')
            print(f'name: {file_data["name"]}')

            searched_mds = [md for md in exist_md_objs if getattr(md.store, f"store_name_{mt_str}") == file_data["name"]]

            # media_data用ーーー
            url = file_data["url"][:1000]
            collected = file_data["collected"]
            try:
                rate = file_data["rate"]
            except Exception:
                rate = 0
            try:
                review_count = file_data["review_count"]
            except Exception:
                review_count = 0

            md_obj: models.Media_data
            if searched_mds:
                if len(searched_mds) >= 2:  # エラーパターン 重複店名
                    print(f'エラーパターン 重複店名 同store_name_{mt_str}')
                    print([md.store.store_name for md in searched_mds])
                    # dupli_names.append([f"dupliエラー:{md.store.store_name}" for md in searched_mds] + ["\n"])
                    # raise Exception()

                    # 重複店舗はとりあえずそれぞれにデータ入れる
                    try:
                        inspection_dict[file_data["name"]] += 1
                    except KeyError:
                        inspection_dict[file_data["name"]] = 0

                    md_obj = searched_mds[inspection_dict[file_data["name"]]]
                else:
                    md_obj = searched_mds[0]

                # media_data用ーーー
                md_obj.url = url
                md_obj.collected = collected
                md_obj.rate = rate
                md_obj.review_count = review_count

                bulk_update_md_list.append(md_obj)
                print('set md to bulk_update_list')

                # review削除用idリスト
                rev_objs = models.Review.objects.filter(media=md_obj).only("pk")
                bulk_delete_list += [r.pk for r in rev_objs]
            else:
                try:
                    file_data["origin_name"]
                    st_obj = next((st for st in used_st_list if getattr(st, "store_name") == file_data["origin_name"]), None)
                except KeyError:
                    st_obj = next((st for st in used_st_list if getattr(st, f"store_name_{mt_str}") == file_data["name"]), None)
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

        # md_objs_after_create = models.Media_data.objects.select_related("store").filter(store__area__area_name="東京都 秋葉原", media_type__media_type="gn")
        # searched_mds = [md for md in md_objs_after_create if getattr(md.store, f"store_name_gn") == "一軒め酒場 神田南口"]

        # review処理ーーーーーーーーーーー
        md_objs_after_create = models.Media_data.objects.select_related("store").filter(store__in=used_st_list, media_type=mt_obj)
        inspection_dict: dict[str, int] = {}
        for enum, file_data in enumerate(jfile):
            file_data["name"] = file_data["name"][:100]
            print(f'\nあと {jfile_length - enum}')

            searched_mds = [md for md in md_objs_after_create if getattr(md.store, f"store_name_{mt_str}") == file_data["name"]]

            print(f'name: {file_data["name"]}')
            print(searched_mds)

            if not searched_mds:
                # errorlist.append(f"not searched_mds: {file_data['name']}")
                continue
            else:
                if len(searched_mds) >= 2:  # エラーパターン 重複店名
                    # 重複店舗はとりあえずそれぞれにデータ入れる
                    try:
                        inspection_dict[file_data["name"]] += 1
                    except KeyError:
                        inspection_dict[file_data["name"]] = 0

                    md_obj = searched_mds[inspection_dict[file_data["name"]]]
                else:
                    md_obj = searched_mds[0]

                try:
                    file_data["review"]
                except KeyError:
                    continue
                try:
                    already_rev_list = []

                    for rev in file_data["review"]:

                        if rev["content"] in already_rev_list:
                            continue

                        title, content, date, log_num, review_point = my_module.make_rev_parts(rev)
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
                        already_rev_list.append(rev["content"])

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
            total_rate = sub.setTotalRateForStore(store_md)
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
        filename = "/".join([os.path.basename(file) for file in file_list])
        subprocess.run(['noti', "-t", "next.あとでプロセス", "-m", f"{filename}"])
        _created_list, not_adopted_list, doubt_list, closed_list, names_for_second_attack, dupli_names, errorlist, updated_names_at_atode = my_module.atode_process(
            atode_list, mt_obj, area_obj, dupli_names, errorlist, doubt_list, updated_name_list, names_for_second_attack, is_atode_file, created_list)

        created_list += _created_list

        print('作成は、')
        pp(created_list)
        print('不採用は、')
        pp(not_adopted_list)

        if closed_list:
            # 既存のファイルの末尾が改行になってるか
            try:
                with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "r") as f:
                    reads = f.read()[-1]
            except Exception:
                reads = "\n"
            with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "a") as f:
                if reads == "\n":
                    f.write("\n".join(closed_list))
                else:
                    f.write("\n")
                    f.write("\n".join(closed_list))
            print('closed_list作成')

        # 2回転目ーーーーーーーーーーーーーーー
        if names_for_second_attack:
            store_objs = store_objs.exclude(store_name__in=updated_names_at_atode)
            print('強くてニューゲーム')
            insert_from_json(file_list, area1, area2, mt_str, doubt_list=doubt_list, names_for_second_attack=names_for_second_attack, store_objs=store_objs, created_list=created_list)
        # 2回転目ーーーーーーーーーーーーーーー

    if doubt_list:
        # n = datetime.datetime.now() + datetime.timedelta(hours=9)
        n = datetime.datetime.now()
        with open(f"/Users/yutakakudo/Google ドライブ/colab/json/doubt_{mt_str}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
            for line in doubt_list:
                f.write(f"{line}\n")
                if "DBの名前" in line or "生還" in line:
                    f.write("\n")
        print('doubt_list作成！')

    if dupli_names:
        def get_unique_list(seq):  # 重複を除外
            seen = []
            return [x for x in seq if x not in seen and not seen.append(x)]
        dupli_names = get_unique_list(dupli_names)
        dupli_names = sum(dupli_names, [])  # リスト1元化
        duplicated_by_google_memo(dupli_names, area1, area2)

    if errorlist:
        n = datetime.datetime.now()  # + datetime.timedelta(hours=9)
        FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), f"var/log/atode_error_log{n.strftime('%Y-%m-%d_%H%M')}.txt")
        with open(FILENAME, "w") as f:
            f.write("\n".join(errorlist))
        print('write エラーログ')

    if mt_str == "uber" and created_list:
        created_list = list(set(created_list))
        n = datetime.datetime.now()
        with open(f"/Users/yutakakudo/Google ドライブ/colab/json/doubtUber_{mt_str}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
            f.write("\n".join(created_list))
        print('doubt_list作成！')

    # エリア別登録数、登録------------
    area_obj.registed = len(models.Store.objects.filter(area=area_obj))
    area_obj.save()
    print(f'{area_obj.area_name}エリア 登録数「{area_obj.registed}」になりました。')


# if __name__ == "__main__":
#     insert_from_json_tb()
