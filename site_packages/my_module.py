import datetime
import os
from decimal import Decimal
from scrape import models
from devtools import debug
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from janome.tokenfilter import *
from janome.charfilter import *
from janome.analyzer import Analyzer
from janome.tokenizer import Tokenizer
import difflib
import re
# import pykakasi
from dateutil.relativedelta import relativedelta


from site_packages.sub import category_set, name_set, address_set, chain_replace, setTotalRateForStore
from scrape.scrape_kit import duplicated_by_google_memo


def collectStoreOtherThanThat(area_name, media_type):
    area_obj = models.Area.objects.get(area_name=area_name)
    sts = models.Store.objects.filter(area=area_obj)
    # sts = models.Store.objects.filter(area=area_obj)[:10]

    to_collect = []
    length = len(sts)
    for storeobj in sts:
        print(f"あと{length}")
        mds = models.Media_data.objects.only('media_type').filter(store=storeobj)
        if not [md for md in mds if md.media_type.__str__() == media_type]:
            print(storeobj.store_name)
            to_collect.append(getattr(storeobj, "store_name"))

        length -= 1
    print(to_collect)

    return to_collect


def capture(driver):
    n = datetime.datetime.now()
    FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"static/images/screen{n.strftime('%Y-%m-%d_%H%M')}.png")
    w = driver.execute_script('return document.body.scrollWidth;')
    h = driver.execute_script('return document.body.scrollHeight;')
    driver.set_window_size(w, h)
    driver.save_screenshot(FILENAME)


class Wait_located:
    def __init__(self, driver):
        self.driver = driver

    def wait_lacated_id(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, value)))

    def wait_lacated_xpath(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, value)))

    def wait_lacated_link_text(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, value)))

    def wait_lacated_partial_link_text(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, value)))

    def wait_lacated_name(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, value)))

    def wait_lacated_tag_name(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, value)))

    def wait_lacated_class_name(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, value)))

    def wait_lacated_css_selector(self, value: str):
        return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, value)))


class Compare_storeName:
    def __init__(self):
        char_filters = [UnicodeNormalizeCharFilter()]  # 半角 → 全角 等
        token_filters = [LowerCaseFilter(), ExtractAttributeFilter('surface')]  # 小文字に ＆ 抽出する属性
        self.a = Analyzer(char_filters=char_filters, token_filters=token_filters)
        # self.kakasi = pykakasi.kakasi()

    def search_store_name(self, store_name: str, querysets, ignore_list: list = None, media: str = "", min_ratio: float = 0.6, origin_name: str = ""):
        if ignore_list is None:
            ignore_list = []

        def make_clean(store_name: str, ignore_list: list) -> str:
            for s in re.findall(r"【.*?】", store_name):  # 【...】を除去
                store_name = store_name.replace(s, '')
            for s in re.findall(r"-.*?-", store_name):  # 【...】を除去
                store_name = store_name.replace(s, '')

            analyzed_name: str = "".join(list(self.a.analyze(store_name)))
            for w in ignore_list:
                analyzed_name = analyzed_name.replace(w, '')

            # # 比較のため日本語はローマ字表記にする。もともと英語の名前なら変化なし
            # converted = self.kakasi.convert(analyzed_name)
            # analyzed_name = "".join([s["hepburn"] for s in converted])
            return analyzed_name

        clean_name = make_clean(store_name, ignore_list)

        store_kouho_dict = {}

        if origin_name:  # google用
            clean_name_in_db = make_clean(origin_name, ignore_list)
            ratio = difflib.SequenceMatcher(lambda x: x in [" ", "-"], clean_name, clean_name_in_db).ratio()  # 類似度
            if ratio >= min_ratio:
                store_kouho_dict.update({querysets: {"ratio": ratio, "clean_name": clean_name, "clean_name_in_db": clean_name_in_db}})
        else:
            # for obj in querysets:
            for obj in querysets:
                clean_name_roma = ""
                try:
                    if media == "":
                        clean_name_in_db = make_clean(obj.store_name, ignore_list)
                        if obj.yomi_roma:
                            clean_name_roma = make_clean(obj.yomi_roma, ignore_list)
                    elif media == "gn":
                        clean_name_in_db = make_clean(obj.store_name_gn, ignore_list)
                    elif media == "hp":
                        clean_name_in_db = make_clean(obj.store_name_hp, ignore_list)
                    elif media == "tb":
                        clean_name_in_db = make_clean(obj.store_name_tb, ignore_list)
                    elif media == "retty":
                        clean_name_in_db = make_clean(obj.store_name_retty, ignore_list)
                    elif media == "demaekan":
                        clean_name_in_db = make_clean(obj.store_name_demaekan, ignore_list)
                    elif media == "uber":
                        clean_name_in_db = make_clean(obj.store_name_uber, ignore_list)
                    elif media == "google":
                        clean_name_in_db = make_clean(obj.store_name_google, ignore_list)
                    else:
                        raise Exception('media が間違っています。')
                except Exception:  # 新しいメディアからの初期登録時。make_clean()の引数がNoneだとエラー
                    clean_name_in_db = ""

                ratio, ratio2 = 0, 0
                if clean_name_in_db:
                    ratio = difflib.SequenceMatcher(lambda x: x in [" ", "-"], clean_name, clean_name_in_db).ratio()  # 類似度
                if clean_name_roma:
                    ratio2 = difflib.SequenceMatcher(lambda x: x in [" ", "-"], clean_name, clean_name_roma).ratio()  # 類似度

                ratio = max([ratio, ratio2])

                if ratio >= min_ratio:
                    store_kouho_dict.update({obj: {"ratio": ratio, "clean_name": clean_name, "clean_name_in_db": clean_name_in_db}})

        # return dict(zip(store_kouho_list, ratio_list))
        return store_kouho_dict


compare = Compare_storeName()


def store_model_process(area_obj: models.Area, media_type: str, store_name: str, ignore_list: list, phone: str = "", address: str = "", category_list: list = None, yomigana: str = "", yomi_roma: str = "", first_time: bool = False, origin_name: str = ""):

    _atode_flg = False
    _atode_dict = {}
    _created_list = []
    _chain_list = []

    if origin_name:
        print(f'origin: {origin_name}')
        try:
            store_objs = models.Store.objects.get(store_name=origin_name, area=area_obj)
        except Exception:
            return None, None, None, None, None
    else:
        store_objs = models.Store.objects.filter(area=area_obj)

    def regist_new():
        store_obj, _ = models.Store.objects.get_or_create(store_name=store_name, area=area_obj)

        name_set(store_obj, store_name, media_type, yomigana, yomi_roma)

        if phone:  # 電話は不用意に変えたくないので新規登録時だけ
            store_obj.phone_number = phone
            store_obj.save()

        address_set(store_obj, address, media_type)

        # カテゴリ登録
        if category_list:
            category_set(store_obj, category_list)

        _created_list.append(store_name)
        print('create store_obj!!')

        return store_obj, _created_list

    if first_time:
        # if first_time or media_type == "tb":
        print('Its a first time!!!')
        store_obj, _created_list = regist_new()
        return store_obj, _atode_flg, _atode_dict, _created_list, _chain_list

    print('first_attack!')
    store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media=media_type, min_ratio=1, origin_name=origin_name)  # mediaごとの名前で照会。同じメディアでも名前が微妙に変わることがあるので完全一致で探さない。← やっぱり完全一致で。
    if store_kouho_dict:
        # debug(store_kouho_dict)
        store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

        # debug(store_obj, store_name, media_type, yomigana, yomi_roma) # 検証用

        name_set(store_obj, store_name, media_type, yomigana, yomi_roma)
        address_set(store_obj, address, media_type)

        # カテゴリ登録
        if category_list:
            category_set(store_obj, category_list)

        print('get store_obj!!')

    else:
        print('second_attack!')
        store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=1, origin_name=origin_name)  # 今度はDB内の名前で照会
        if store_kouho_dict:
            debug(store_kouho_dict)
            store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

            name_set(store_obj, store_name, media_type, yomigana, yomi_roma)
            address_set(store_obj, address, media_type)

            # カテゴリ登録
            if category_list:
                category_set(store_obj, category_list)

            print('get store_obj and update!!')
        else:
            # チェーン店の場合、メディアにより多少変わるので名前を替えて再検索
            replaced_name: str = chain_replace(store_name)
            if replaced_name:
                _chain_list.append(replaced_name)
                print('chain_attack!!!!')
                store_kouho_dict = compare.search_store_name(replaced_name, store_objs, ignore_list, media='', min_ratio=1, origin_name=origin_name)
                if store_kouho_dict:
                    debug(store_kouho_dict)
                    store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

                    name_set(store_obj, store_name, media_type, yomigana, yomi_roma)
                    address_set(store_obj, address, media_type)

                    # カテゴリ登録
                    if category_list:
                        category_set(store_obj, category_list)

                    print('get store_obj and update!!')
                    return store_obj, _atode_flg, _atode_dict, _created_list, _chain_list

            print('third_attack!')
            store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=0.3, origin_name=origin_name)  # 今度はDB内の名前で照会

            if origin_name:
                store_obj: models.Store = store_objs
                print('atode...')
                _atode_flg = True
                _atode_dict["store_name_db"] = store_obj.store_name
                _atode_dict["store_name_site"] = store_name

                # あれば。なければ明示的にNoneをいれてる。
                _atode_dict["address_db"] = store_obj.address if store_obj.address else None
                _atode_dict["address_site"] = address if address else None
                _atode_dict["phone"] = phone if phone else None
                _atode_dict["category"] = category_list if category_list else None
                _atode_dict["yomigana"] = yomigana if yomigana else None
                _atode_dict["yomi_roma"] = yomi_roma if yomi_roma else None

            elif store_kouho_dict:
                # debug(store_kouho_dict)
                store_obj, sub_name_dict = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得
                debug("似てる名前", store_obj.store_name, sub_name_dict)

                # 同メディアの名前があればスキップして新規作成
                if getattr(store_obj, f"store_name_{media_type}"):
                    if not media_type == "hp":
                        new_store_obj, _created_list = regist_new()
                        return new_store_obj, _atode_flg, _atode_dict, _created_list, _chain_list
                    # HPだけあやしい
                    else:
                        _atode_dict["this_media_name"] = getattr(store_obj, f"store_name_{media_type}")
                    # _atode_dict["this_media_name"] = getattr(store_obj, f"store_name_{media_type}")

                # あるか無いか微妙なラインなのでatodeシリーズにまとめで確認
                print('atode...')
                _atode_flg = True
                _atode_dict["store_name_db"] = store_obj.store_name
                _atode_dict["store_name_site"] = store_name
                # _atode_dict["clean_name"] = sub_name_dict["clean_name"]
                # _atode_dict["clean_name_in_db"] = sub_name_dict["clean_name_in_db"]

                # あれば。なければ明示的にNoneをいれてる。
                _atode_dict["address_db"] = store_obj.address if store_obj.address else None
                _atode_dict["address_site"] = address if address else None
                _atode_dict["phone"] = phone if phone else None
                _atode_dict["category"] = category_list if category_list else None
                _atode_dict["yomigana"] = yomigana if yomigana else None
                _atode_dict["yomi_roma"] = yomi_roma if yomi_roma else None

            else:
                store_obj, _created_list = regist_new()

    return store_obj, _atode_flg, _atode_dict, _created_list, _chain_list


def atode_process(atode_list: list, mt_obj: models.Media_type, area_obj: models.Area, updated_name_list: list = None):
    mt_str: str = mt_obj.media_type
    errorlist = []

    _created_list = []
    not_adopted_list = []

    update_list = []
    regist_list = []

    doubt_list = []
    kill_list = []

    # debug(atode_list)

    length = len(atode_list)
    for store in atode_list:
        print(' ')
        # print(f'この名前: {store["store_name_site"]}  \nDBの名前: {store["store_name_db"]}\nclean   : {store["clean_name"]}\nclean_db: {store["clean_name_in_db"]}')
        try:
            print(f'この住所    : {store["address_site"]}')
            print(f'DBの住所    : {store["address_db"]}')
            print(' ')
        except Exception:
            pass
        print(f'この名前    : {store["store_name_site"]}')
        try:
            print(f'同メディア名: {store["this_media_name"]}')
        except Exception:
            pass
        print(f'DBの名前    : {store["store_name_db"]}')

        length -= 1
        print(f"あと {length}")

        def submit_regist(doubt=None):
            regist = input('新規登録しますか？y / N: ').lower()
            if regist == "y":
                regist_list.append(store)
                if doubt:
                    doubt_list.append(f'この名前    : {store["store_name_site"]}')
                    doubt_list.append(f'DBの名前    : {store["store_name_db"]}')

            elif regist == "n":  # ゴミ箱いき
                not_adopted_list.append(store["store_name_site"])
                if doubt:
                    doubt_list.append(f'この名前    : {store["store_name_site"]}')
                    doubt_list.append(f'DBの名前    : {store["store_name_db"]}')
                print('move not_adopted_list')
            else:  # やり直し
                if doubt:
                    return submit_regist(doubt=True)
                else:
                    return submit_regist()

        def submit_update():
            submit = input('この名前ですか？y / N or j or K： ').lower()
            if submit == "y":
                update_list.append(store)

            elif submit == "n":
                submit_regist()

            elif submit == "j":
                submit_regist(doubt=True)

            elif submit == "k":
                kill_list.append(store["store_name_db"])
                print('kill')

            else:
                return submit_update()
        submit_update()

    def update_or_regist(datalist, flg: str):
        bulk_review_list = []
        bulk_delete_list = []
        length = len(datalist)

        store_objs = models.Store.objects.filter(area=area_obj)
        if flg == "regist":
            # store一括登録ーーーーーーーーー
            name_list = [store["store_name_site"] for store in datalist]
            exist_objs = store_objs.filter(store_name__in=name_list).only('store_name')
            exist_list = [st.store_name for st in exist_objs]
            name_list = [s for s in name_list if s not in exist_list]

            bulk_create_store_list = []
            for store_name in name_list:
                st_obj = models.Store(
                    store_name=store_name,
                    area=area_obj
                )
                bulk_create_store_list.append(st_obj)

            models.Store.objects.bulk_create(bulk_create_store_list)
            # ーーーーーーーーーーーーーーーー

        st_obj_list = []

        for i, store in enumerate(datalist):
            print(f'store処理 あと {length-i}')
            store_obj: models.Store
            if flg == "update":
                store_obj = [s for s in store_objs if s.store_name == store["store_name_db"]][0]
            elif flg == "regist":
                store_obj = [s for s in store_objs if s.store_name == store["store_name_site"]][0]
            else:
                # store_obj = models.Store.objects.none()
                print('エラー')
                raise Exception()

            name_set(store_obj, store["store_name_site"], mt_str, store["yomigana"], store["yomi_roma"])

            # 電話
            if store["phone"] and not store_obj.phone_number:
                store_obj.phone_number = store["phone"]

            # 住所
            if (store["address_site"] and not store_obj.address) or (store["address_site"] and mt_str == "gn") or (store["address_site"] and mt_str == "tb"):
                store_obj.address = store["address_site"]

            # カテゴリ登録
            if store["category"]:
                category_set(store_obj, store["category"], errorlist)

            st_obj_list.append(store_obj)

        models.Store.objects.bulk_update(st_obj_list, ["phone_number", "address"])
        print('bulk store補足')

        md_objs = models.Media_data.objects.select_related("store", "media_type").filter(store__in=st_obj_list)
        # media_data登録ーーーーーーーーーーーーーー
        bulk_create_media_list = []
        exist_objs = md_objs.filter(media_type=mt_obj)
        # exist_objs = md_objs.filter(media_type=mt_obj).only('store')
        exist_list = [md.store for md in exist_objs]
        bulk_st_obj_list = [st for st in st_obj_list if st not in exist_list]
        for st_obj in bulk_st_obj_list:
            md_obj = models.Media_data(
                store=st_obj,
                media_type=mt_obj
            )
            bulk_create_media_list.append(md_obj)
        models.Media_data.objects.bulk_create(bulk_create_media_list)
        # ーーーーーーーーーーーーーーーーーーーー

        for i, store in enumerate(datalist):
            print(f'md処理 あと {length-i}')

            md_obj: models.Media_data
            searched_mds = [md for md in md_objs if getattr(md.store,f"store_name_{mt_str}") == store["store_name_site"] and md.media_type == mt_obj]
            
            if len(searched_mds) >= 2: # エラーパターン 重複店名
                print(f'エラーリスト追加 同store_name_{mt_str} {store["store_name_site"]}')
                errorlist.append((f'エラー 同store_name_{mt_str} {store["store_name_site"]}',[md.store.store_name for md in searched_mds]))

            md_obj = searched_mds[0]

            # ??????????????????????????
            # if flg == "update":
            #     md_obj = [md for md in md_objs if getattr(md.store,f"store_name_{mt_str}") == store["store_name_db"] and md.media_type == mt_obj][0]
            # elif flg == "regist":
            #     md_obj = [md for md in md_objs if md.store.store_name == store["store_name_site"] and md.media_type == mt_obj][0]
            # else:
            #     # md_obj = models.Store.objects.none()
            #     print('エラー')
            #     raise Exception()

            if store["collected"]:
                try:
                    md_obj.collected = store["collected"]
                    md_obj.save()
                except Exception as e:
                    errorlist.append((type(e), e, store["collected"]))

            try:
                md_obj.rate = store["rate"]
                md_obj.save()
            except Exception as e:
                errorlist.append((type(e), e, store["rate"]))

            try:
                md_obj.url = store["url"]
                md_obj.save()
            except KeyError as e:
                errorlist.append((type(e), e, store["url"]))

            try:
                md_obj.review_count = store["review_count"]
                md_obj.save()
            except KeyError as e:
                errorlist.append((type(e), e, store["review_count"]))

            # review登録ーーーーーーーー
            if flg == "update":
                # データ消して刷新
                rev_objs = models.Review.objects.filter(media=md_obj).only("pk")
                bulk_delete_list += [r.pk for r in rev_objs]

            already_rev_list = []
            for review in store["review"]:
                try:
                    if review["content"] in already_rev_list:
                        continue

                    new_rev_obj = models.Review(
                        title=review["title"],
                        content=review["content"],
                        media=md_obj,
                        review_date=review["date"],
                        review_point=review["review_point"],
                        log_num_byTabelog=review["log_num"]
                    )
                    bulk_review_list.append(new_rev_obj)

                    already_rev_list.append(review["content"])

                except Exception as e:
                    print(type(e), e)
                    print(store["store_name_site"])
                    print('レビュー登録失敗↑')
                    errorlist.append((type(e), e, store["store_name_site"], review["title"]))

        # review登録ーーーーーー
        models.Review.objects.filter(pk__in=bulk_delete_list).delete()
        print('bulk削除 レビュー')
        models.Review.objects.bulk_create(bulk_review_list)
        print('bulkクリエイト レビュー')

        # 店ごとのtotal_rate登録ーーーーー
        st_obj_len = len(st_obj_list)
        for i, st in enumerate(st_obj_list):
            print(f'(atode)total_rate登録 あと {st_obj_len-i} 店')
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

    from scrape import scrape_kit
    area1 = area_obj.area_name.split(" ")[0]
    area2 = area_obj.area_name.split(" ")[1]
    if update_list:
        try:
            update_or_regist(update_list, flg="update")
        except Exception as e:
            print(type(e), e)
            scrape_kit.generate_json(update_list, mt_str, area1, area2, update_or_regist="update")
    if regist_list:
        try:
            update_or_regist(regist_list, flg="regist")
        except Exception as e:
            print(type(e), e)
            scrape_kit.generate_json(regist_list, mt_str, area1, area2, update_or_regist="regist")

    # 同じ検索結果名からDB内のかぶってる店舗あぶりだす。ほぼgoogle用
    name_site_list = [s["store_name_site"] for s in update_list]
    name_db_list = [s["store_name_db"] for s in update_list]
    if updated_name_list:  # 既に同一nameでupdateしたものも追加
        name_site_list += updated_name_list
        name_db_list += updated_name_list
    import collections
    counter = collections.Counter(name_site_list)
    dupli_site_name = [s for s in counter if counter[s] >= 2]  # 出現回数2以上

    if dupli_site_name:
        dupli_dict = dict(zip(name_db_list, name_site_list))
        dupli_names = []
        for name in dupli_site_name:  # 同じvalue同士の順番でリストに入れたいため
            dupli_names += [k for k, v in dupli_dict.items() if v == name]
            dupli_names += "\n"
        if dupli_names:
            duplicated_by_google_memo(dupli_names, area1, area2)
    # ーーーーーーーーーーーーーーーーーーーーーーーーーーー

    # その名前で検索しても出てこない店を調査。口コミがないなら(又は最終口コミがけっこう前)、既に閉店していると判断。店の削除とIGNORENAMEリストに書き込み。
    closed_list = []
    if kill_list:
        limit_months = 36

        for name in kill_list:
            store_obj = models.Store.objects.get(store_name=name, area=area_obj)
            reviews = models.Review.objects.filter(media__store=store_obj)

            rescue_flg = False
            if reviews:
                for rev in reviews:
                    if rev.review_date > datetime.datetime.now().date() - relativedelta(months=limit_months):
                        rescue_flg = True
                        break

            if rescue_flg is False:
                closed_list.append(name)
            else:
                doubt_list.append(f'生還    : {name}')
        if closed_list:
            delete_objs = models.Store.objects.filter(store_name__in=closed_list, area=area_obj)
            delete_objs.delete()
            print(f'delete may be closed store: {closed_list}')
    # ーーーーーーーーーーーーーーーーーーーーーーーーーー

    if errorlist:
        print('write エラーログ')
        n = datetime.datetime.now()  # + datetime.timedelta(hours=9)
        with open(f"/var/log/atode_error_log{n.strftime('%Y-%m-%d_%H%M')}", "w") as f:
            for d in errorlist:
                f.write(f"{d}\n")

    return _created_list, not_adopted_list, doubt_list, closed_list
