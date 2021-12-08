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
from time import sleep
# import pykakasi
from dateutil.relativedelta import relativedelta


from site_packages import sub

import importlib
importlib.reload(sub)
print("モジュールリロード sub")


def collectStoreOtherThanThat(area_name, mt_str: str):
    """
    指定するmediatypeのmediadataがない店の名前を集める
    """
    area_obj = models.Area.objects.get(area_name=area_name)
    # area_obj = models.Area.objects.get(area_name="東京都 秋葉原")
    sts = models.Store.objects.filter(area=area_obj)
    # sts = models.Store.objects.filter(area=area_obj)[:10]

    to_collect = []
    length = len(sts)

    if models.Media_data.objects.filter(media_type__media_type=mt_str, store__area=area_obj).exists():
        all_mds = models.Media_data.objects.select_related('media_type', "store").only('media_type', "store").filter(store__in=sts)

        for enum, st in enumerate(sts):
            print(f"あと{length-enum}")
            filtered_mds = all_mds.filter(store=st)
            if not [md for md in filtered_mds if md.media_type.__str__() == mt_str]:
                print(st.store_name)
                to_collect.append(getattr(st, "store_name"))
    else:
        for enum, st in enumerate(sts):
            print(f"あと{length-enum}")
            to_collect.append(getattr(st, "store_name"))

    # print(to_collect)

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

    def search_store_name(self, store_name: str, store_objs, ignore_list: list = None, media: str = "", min_ratio: float = 0.6):
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

        for obj in store_objs:
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


def store_model_process(store_objs, area_obj: models.Area, media_type: str, store_name: str, ignore_list: list, phone: str = "", address: str = "", category_list: list = None, yomigana: str = "", yomi_roma: str = "", first_time: bool = False, origin_name: str = ""):

    _atode_flg = False
    _atode_dict = {}
    _created_list = []
    _chain_list = []

    def regist_new():
        store_obj, _ = models.Store.objects.get_or_create(store_name=store_name, area=area_obj)

        sub.set_name(store_obj, store_name, media_type, yomigana, yomi_roma)

        if phone:  # 電話は不用意に変えたくないので新規登録時だけ
            store_obj.phone_number = phone
            store_obj.save()

        sub.set_address(store_obj, address, media_type)

        # カテゴリ登録
        if category_list:
            sub.set_category(store_obj, category_list)

        _created_list.append(store_name)
        print('create store_obj!!')

        return store_obj, _created_list

    if first_time:
        # if first_time or media_type == "tb":
        print('Its a first time!!!')
        store_obj, _created_list = regist_new()
        return store_obj, _atode_flg, _atode_dict, _created_list, _chain_list

    print('first_attack!')
    now = datetime.datetime.now()
    store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media=media_type, min_ratio=1)  # mediaごとの名前で照会。同じメディアでも名前が微妙に変わることがあるので完全一致で探さない。← やっぱり完全一致で。
    print("search_store_name所要時間： ", datetime.datetime.now() - now)
    if store_kouho_dict:
        # debug(store_kouho_dict)
        store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

        # debug(store_obj, store_name, media_type, yomigana, yomi_roma) # 検証用

        sub.set_name(store_obj, store_name, media_type, yomigana, yomi_roma)
        sub.set_address(store_obj, address, media_type)

        # カテゴリ登録
        if category_list:
            sub.set_category(store_obj, category_list)

        print('get store_obj!!')

    else:
        print('second_attack!')
        store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=1)  # 今度はDB内の名前で照会
        if store_kouho_dict:
            debug(store_kouho_dict)
            store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

            sub.set_name(store_obj, store_name, media_type, yomigana, yomi_roma)
            sub.set_address(store_obj, address, media_type)

            # カテゴリ登録
            if category_list:
                sub.set_category(store_obj, category_list)

            print('get store_obj and update!!')
        else:
            # チェーン店の場合、メディアにより多少変わるので名前を替えて再検索
            replaced_names: list = sub.chain_replace(store_name)
            if replaced_names:
                for rep_name in replaced_names:
                    print('chain_attack!!!!')
                    store_kouho_dict = compare.search_store_name(rep_name, store_objs, ignore_list, media='', min_ratio=1)
                    if store_kouho_dict:
                        debug(store_kouho_dict)
                        store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

                        sub.set_name(store_obj, store_name, media_type, yomigana, yomi_roma)
                        sub.set_address(store_obj, address, media_type)

                        # カテゴリ登録
                        if category_list:
                            sub.set_category(store_obj, category_list)

                        print('get store_obj and update!!')
                        _chain_list.append(rep_name)

                        return store_obj, _atode_flg, _atode_dict, _created_list, _chain_list

            print('third_attack!')
            store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=0.3)  # 今度はDB内の名前で照会

            if origin_name:
                store_obj: models.Store = store_objs[0]
                print('atode...')
                _atode_flg = True
                _atode_dict["store_name_db"] = origin_name
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
                        print('同メディアの名前発見 → atode処理スキップして新規作成')
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


def atode_process(atode_list: list, mt_obj: models.Media_type, area_obj: models.Area, dupli_names, errorlist: list, doubt_list, updated_name_list: list = None, _names_for_second_attack: list = None, is_atode_file: str = "", _created_list: list = None):
    mt_str: str = mt_obj.media_type
    kill_list = []
    names_for_second_attack = []
    no_change_pairs = []

    if _created_list is None:
        _created_list = []
    if updated_name_list is None:
        updated_name_list = []

    not_adopted_list = []
    update_list = []
    regist_list = []

    if is_atode_file == "update":
        update_list = atode_list
    elif is_atode_file == "regist":
        regist_list = atode_list

    else:
        length = len(atode_list)
        skip_names = []
        for listdata in atode_list:

            # 色付けーーーーーーーーーーーー
            if not _names_for_second_attack:  # 初回のみ
                try:  # なぜか失敗するときがある (<class 're.error'>, error('missing ), unterminated subpattern at position 0')
                    finded_index_site = []
                    finded_index_db = []
                    for enum, s in enumerate(listdata["store_name_site"].lower()):
                        if s == " " or s == "　" or s == "(" or s == ")":
                            continue
                        if s == ".":
                            s = r"\."
                        indexes = [m.start() for m in re.finditer(s, listdata["store_name_db"].lower())]
                        if indexes:
                            finded_index_db += indexes
                            finded_index_site.append(enum)
                    finded_index_db = sorted(list(set(finded_index_db)))

                    store_name_site = listdata["store_name_site"]
                    for index in reversed(finded_index_site):
                        store_name_site = store_name_site[:index] + '\033[45m' + store_name_site[index] + '\033[0m' + store_name_site[index + 1:]
                    store_name_db = listdata["store_name_db"]
                    for index in reversed(finded_index_db):
                        store_name_db = store_name_db[:index] + '\033[45m' + store_name_db[index] + '\033[0m' + store_name_db[index + 1:]
                except Exception as e:
                    print(type(e), e)
                    store_name_site = listdata["store_name_site"]
                    store_name_db = listdata["store_name_db"]
            else:
                store_name_site = listdata["store_name_site"]
                store_name_db = listdata["store_name_db"]
            # ーーーーーーーーーーーー色付け

            print(' ')

            try:
                print(f'この住所    : {listdata["address_site"]}')
                print(f'DBの住所    : {listdata["address_db"]}')
                print(' ')
            except Exception:
                pass
            print(f'この名前    : {store_name_site}')
            try:
                print(f'同メディア名: {listdata["this_media_name"]}')
            except Exception:
                pass
            print(f'DBの名前    : {store_name_db}')

            length -= 1
            print(f"あと {length}")

            # 結果が変わらない場合は
            if _names_for_second_attack:
                name_set = [[name["store_name_site"], name["store_name_db"]] for name in _names_for_second_attack]
                if [listdata["store_name_site"], listdata["store_name_db"]] in name_set:
                    no_change_pairs.append(listdata)
                    print('結果が変わらない')
                    sleep(0.1)
                    continue

            def submit_regist(doubt=False, auto=False):
                regist = input('新規登録しますか？y / N: ').lower()
                if regist == "y":
                    regist_list.append(listdata)
                    if doubt:
                        doubt_list.append(f'この名前    : {listdata["store_name_site"]}')
                        doubt_list.append(f'DBの名前    : {listdata["store_name_db"]}')

                elif regist == "n":  # ゴミ箱いき
                    not_adopted_list.append(listdata["store_name_site"])
                    if doubt:
                        doubt_list.append(f'ゴミ箱いき  : {listdata["store_name_site"]}')
                        doubt_list.append(f'DBの名前    : {listdata["store_name_db"]}')
                    print('move not_adopted_list')
                else:  # やり直し
                    if doubt:
                        return submit_regist(doubt=True)
                    else:
                        return submit_regist()

            def submit_update():
                submit = input('この名前ですか？y / N or J or H or B or S： ').lower()
                if submit == "y":
                    update_list.append(listdata)

                elif submit == "n":
                    submit_regist()

                elif submit == "j":
                    submit_regist(doubt=True)

                elif submit == "h":
                    kill_list.append(listdata["store_name_db"])

                elif submit == "b":  # 次に回す
                    names_for_second_attack.append({"store_name_site": listdata["store_name_site"], "store_name_db": listdata["store_name_db"]})

                elif submit == "s":
                    skip_names.append(listdata["store_name_site"])
                    kill_list.append(listdata["store_name_db"])

                else:
                    return submit_update()

            # 既に使ったdb_nameはnames_for_second_attackへーーーーー
            used_names_this_time = [s["store_name_db"] for s in update_list]
            if listdata["store_name_db"] in (updated_name_list + used_names_this_time):
                names_for_second_attack.append({"store_name_site": listdata["store_name_site"], "store_name_db": listdata["store_name_db"]})
                print(f'既に使ったdb_name {listdata["store_name_db"]}')
                print('☆★☆ ラッキー ☆★☆')
                sleep(0.1)
                print('☆★☆ ラッキー ☆★☆')
                sleep(0.1)

            # skip_name
            elif listdata["store_name_site"] in skip_names:
                kill_list.append(listdata["store_name_db"])
                print("skip name...")

            else:
                submit_update()

        # updateするものがなくなったら諦めてそのターンでregist
        if not update_list and names_for_second_attack:
            names_for_second_attack.clear()
            regist_list += atode_list
            print('オートregist pattern 1')
        # ↓ いらないかも
        # names_for_second_attackがなくなったら諦めてregist
        elif not names_for_second_attack and no_change_pairs:
            regist_list += no_change_pairs
            print('オートregist pattern 2')
            # for store in no_change_pairs:
            # doubt_list.append(f'オートregist: {store["store_name_site"]}')
            # doubt_list.append(f'DBの名前    : {store["store_name_db"]}')
            # print(f'オートregist_list in {store["store_name_site"]}')

    def update_or_regist(datalist, flg: str):
        length = len(datalist)
        _dupli_names = []

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
                _created_list.append(store_name)

            models.Store.objects.bulk_create(bulk_create_store_list)
            print("store一括登録OK")
            store_objs = models.Store.objects.filter(area=area_obj)
            # ーーーーーーーーーーーーーーーー

        used_st_list = []

        for i, listdata in enumerate(datalist):
            print(f'{flg} store処理 あと {length-i}')
            store_obj: models.Store
            if flg == "update":
                store_obj = [s for s in store_objs if s.store_name == listdata["store_name_db"]][0]
            elif flg == "regist":
                store_obj = [s for s in store_objs if s.store_name == listdata["store_name_site"]][0]
            else:
                # store_obj = models.Store.objects.none()
                print('エラー')
                raise Exception()

            sub.set_name(store_obj, listdata["store_name_site"], mt_str, listdata["yomigana"], listdata["yomi_roma"])

            # 電話
            if listdata["phone"] and not store_obj.phone_number:
                store_obj.phone_number = listdata["phone"]

            # 住所
            if (listdata["address_site"] and not store_obj.address) or (listdata["address_site"] and mt_str == "gn") or (listdata["address_site"] and mt_str == "tb"):
                store_obj.address = listdata["address_site"]

            # カテゴリ登録
            if listdata["category"]:
                sub.set_category(store_obj, listdata["category"])

            used_st_list.append(store_obj)

        models.Store.objects.bulk_update(used_st_list, ["phone_number", "address"])
        print('bulk store補足')

        # media_data登録ーーーーーーーーーーーーーー
        exist_md_objs = models.Media_data.objects.select_related("store", "media_type").filter(store__in=used_st_list, media_type=mt_obj)

        bulk_update_md_list = []
        bulk_create_md_list = []
        bulk_delete_list = []
        bulk_review_list = []
        dupli_names = []
        inspection_dict: dict[str, int] = {}

        for i, listdata in enumerate(datalist):
            print(f'{flg} md処理 あと {length-i}')
            print(f'name: {listdata["store_name_site"]}')

            searched_mds = [md for md in exist_md_objs if getattr(md.store, f"store_name_{mt_str}") == listdata["store_name_site"]]

            url = listdata["url"][:1000]
            collected = listdata["collected"]
            try:
                rate = listdata["rate"]
            except Exception:
                rate = 0
            try:
                review_count = listdata["review_count"]
            except Exception:
                review_count = 0

            md_obj: models.Media_data
            if searched_mds:
                if len(searched_mds) >= 2:  # エラーパターン 重複店名
                    print(f'dupliエラー 同store_name_{mt_str} {listdata["store_name_site"]}')
                    print([md.store.store_name for md in searched_mds])
                    # errorlist.append(f"エラー 同store_name_{mt_str} {listdata['store_name_site']}, {[md.store.store_name for md in searched_mds]}")
                    # _dupli_names.append([f"dupliエラー:{md.store.store_name}" for md in searched_mds]+["\n"])

                    # 重複店舗はとりあえずそれぞれにデータ入れる
                    try:
                        inspection_dict[listdata["store_name_site"]] += 1
                    except KeyError:
                        inspection_dict[listdata["store_name_site"]] = 0

                    md_obj = searched_mds[inspection_dict[listdata["store_name_site"]]]
                else:
                    md_obj = searched_mds[0]

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

                searched_sts = [st for st in used_st_list if getattr(st, f"store_name_{mt_str}") == listdata["store_name_site"]]

                if len(searched_sts) >= 2:  # エラーパターン 重複店名
                    print(f'dupliエラー 同store_name_{mt_str} {listdata["store_name_site"]}')
                    print([st.store_name for st in searched_sts])
                    # errorlist.append(f"エラー 同store_name_{mt_str} {listdata['store_name_site']}, {[md.store.store_name for md in searched_sts]}")
                    # _dupli_names.append([f"dupliエラー:{md.store.store_name}" for md in searched_sts]+["\n"])

                    # 重複店舗はとりあえずそれぞれにデータ入れる
                    try:
                        inspection_dict[listdata["store_name_site"]] += 1
                    except KeyError:
                        inspection_dict[listdata["store_name_site"]] = 0

                    st_obj = searched_sts[inspection_dict[listdata["store_name_site"]]]
                else:
                    st_obj = searched_sts[0]

                # if st_obj:
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

        if bulk_create_md_list:
            models.Media_data.objects.bulk_create(bulk_create_md_list)
            print('bulk_create_md_list')

        # review処理ーーーーーーーーーーー
        md_objs_after_create = models.Media_data.objects.select_related("store").filter(store__in=used_st_list, media_type=mt_obj)
        inspection_dict: dict[str, int] = {}
        for enum, listdata in enumerate(datalist):
            print(f'\nreview処理 あと {length - enum}')

            searched_mds = [md for md in md_objs_after_create if getattr(md.store, f"store_name_{mt_str}") == listdata["store_name_site"]]

            print(f'name: {listdata["store_name_site"]}')

            if len(searched_mds) >= 2:  # エラーパターン 重複店名
                # 重複店舗はとりあえずそれぞれにデータ入れる
                try:
                    inspection_dict[listdata["store_name_site"]] += 1
                except KeyError:
                    inspection_dict[listdata["store_name_site"]] = 0

                md_obj = searched_mds[inspection_dict[listdata["store_name_site"]]]
            else:
                md_obj = searched_mds[0]

            already_rev_list = []

            for rev in listdata["review"]:
                # try:
                if rev["content"] in already_rev_list:
                    continue

                print(rev["date"], rev["content"][:20])

                new_rev_obj = models.Review(
                    media=md_obj,
                    title=rev["title"],
                    content=rev["content"],
                    review_date=rev["date"],
                    review_point=rev["review_point"],
                    log_num_byTabelog=rev["log_num"],
                )
                bulk_review_list.append(new_rev_obj)

                already_rev_list.append(rev["content"])

                # except Exception as e:
                #     print(type(e), e)
                #     print(listdata["store_name_site"])
                #     print('レビュー登録失敗↑')
                #     errorlist.append(f"{type(e)}, {e}, {listdata['store_name_site']}, {review['title']}")

        # review登録ーーーーーー
        if bulk_delete_list:
            models.Review.objects.filter(pk__in=bulk_delete_list).delete()
            print('bulk削除 レビュー')
        if bulk_review_list:
            models.Review.objects.bulk_create(bulk_review_list)
            print('bulkクリエイト レビュー')

        # 店ごとのtotal_rate登録ーーーーー
        st_obj_len = len(used_st_list)
        for i, st in enumerate(used_st_list):
            print(f'{flg} total_rate登録 あと {st_obj_len-i} 店')
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

        return _dupli_names

    from scrape import scrape_kit
    area1 = area_obj.area_name.split(" ")[0]
    area2 = area_obj.area_name.split(" ")[1]
    if update_list:
        try:
            _dupli_names = update_or_regist(update_list, flg="update")
            dupli_names += _dupli_names
        except Exception as e:
            print(type(e), e)
            scrape_kit.generate_json(update_list, mt_str, area1, area2, update_or_regist="update")
    if regist_list:
        try:
            _dupli_names = update_or_regist(regist_list, flg="regist")
            dupli_names += _dupli_names
        except Exception as e:
            print(type(e), e)
            scrape_kit.generate_json(regist_list, mt_str, area1, area2, update_or_regist="regist")

    # 同じ検索結果名からDB内のかぶってる店舗あぶりだす。ほぼgoogle用
    name_site_list = [s["store_name_site"] for s in update_list + regist_list]
    name_db_list = [s["store_name_db"] for s in update_list + regist_list]
    if updated_name_list:  # 既に同一nameでupdateしたものも追加
        name_site_list += updated_name_list
        name_db_list += updated_name_list
    import collections
    counter = collections.Counter(name_site_list)
    dupli_site_name = [s for s in counter if counter[s] >= 2]  # 出現回数2以上

    if dupli_site_name:
        dupli_dict = dict(zip(name_db_list, name_site_list))
        # dupli_names = []
        for name in dupli_site_name:  # 同じvalue同士の順番でリストに入れたいため
            dupli_names.append([k for k, v in dupli_dict.items() if v == name] + ["\n"])
    # ーーーーーーーーーーーーーーーーーーーーーーーーーーー

    # その名前で検索しても出てこない店を調査。口コミがないなら(又は最終口コミがけっこう前)、既に閉店していると判断。店の削除とIGNORENAMEリストに書き込み。
    closed_list = []
    if kill_list:
        limit_months = 36

        length = len(kill_list)
        for enum, name in enumerate(kill_list):
            print(f'\nあと {length-enum}')
            print(name)
            # store_obj = models.Store.objects.get(store_name=name, area=area_obj)
            md_objs = models.Media_data.objects.filter(store__store_name=name, store__area=area_obj)
            reviews = models.Review.objects.filter(media__in=md_objs)

            rescue_flg = False
            if md_objs.count() >= 2:
                rescue_flg = True
            else:
                if reviews:
                    for rev in reviews:
                        if rev.review_date > datetime.datetime.now().date() - relativedelta(months=limit_months):
                            rescue_flg = True
                            break

            if rescue_flg is False:
                closed_list.append(name)
                print('kill..')
            else:
                doubt_list.append(f'生還    : {name}')
                print('rescue!!')
            # doubt_list.append(f'生還    : {name}')
            # # print('rescue!!')

        if closed_list:
            delete_objs = models.Store.objects.filter(store_name__in=closed_list, area=area_obj)
            delete_objs.delete()
            print(f'delete may be closed store: {closed_list}')
    # ーーーーーーーーーーーーーーーーーーーーーーーーーー

    if names_for_second_attack and no_change_pairs:
        names_for_second_attack += [{"store_name_site": store["store_name_site"], "store_name_db": store["store_name_db"]} for store in no_change_pairs]
        print('names_for_second_attack add no_change_pairs')

    updated_names_at_atode = []
    if update_list:
        updated_names_at_atode += [s["store_name_db"] for s in update_list]
    if regist_list:
        updated_names_at_atode += [s["store_name_site"] for s in regist_list]

    return _created_list, not_adopted_list, doubt_list, closed_list, names_for_second_attack, dupli_names, errorlist, updated_names_at_atode


def make_rev_parts(rev):
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
    return title, content, date, log_num, review_point
