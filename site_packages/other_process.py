
from send2trash import send2trash
from difflib import SequenceMatcher
import pyperclip
from glob import glob
from scrape import models
from site_packages import sub
from decimal import Decimal
import datetime
import pykakasi
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from scrape import driver_settings, models


# searched_mds = models.Media_data.objects.filter(store__in= models.Store.objects.filter(store_name_google="シャンパンバー シュッ!"),media_type__media_type="google")

# media_dataのないstoreを掃除ーーーーーーーーー


def clean_store_obj(area_obj):
    # store_objs = models.Store.objects.all()
    store_objs = models.Store.objects.filter(area__area_name="千葉県 船橋市")
    count = store_objs.count()
    destroy = []
    destroy_name = []
    now = datetime.datetime.now()
    for s in store_objs:
        if len(models.Media_data.objects.filter(store=s)) == 0:
            print(s.store_name)
            destroy.append(s.pk)
            destroy_name.append(s.store_name)
        print(f"count あと {count}")
        count -= 1
    models.Store.objects.filter(pk__in=destroy).delete()
    sa = datetime.datetime.now() - now
    print("destroy are ", destroy_name)
    print(sa)

    # 確認のみ
    from pprint import pprint as pp
    # be_deleted = [[s.store_name, s.area.__str__()] for s in store_objs if len(models.Media_data.objects.filter(store=s)) == 0] # 内包表記でやっても時間変わらなかった
    be_deleted = []
    for s in store_objs:
        if len(models.Media_data.objects.filter(store=s)) == 0:
            be_deleted.append(s)
        print(f"count あと {count}")
        count -= 1
    pp(be_deleted)


# 重複を統合ーーーーーーーーーー
def conflict_integration(childname, childmedia, parentname, area=""):
    if not area:
        child_obj = models.Store.objects.get(store_name=childname)
    else:
        child_obj = models.Store.objects.get(store_name=childname, area__area_name=area)
    # target_store_name_by_media = getattr(child_obj, f"store_name_{childmedia}")
    child_m_type_obj = models.Media_type.objects.get(media_type=childmedia)
    child_m_data_obj = models.Media_data.objects.get(store=child_obj, media_type=child_m_type_obj)
    child_r_objs = models.Review.objects.filter(media=child_m_data_obj)

    # 親
    if not area:
        parent_obj = models.Store.objects.get(store_name=parentname)
    else:
        parent_obj = models.Store.objects.get(store_name=parentname, area__area_name=area)

    print(child_obj)
    print(parent_obj)

    # 名前ーーーーーーーーーー
    # ？？？？？？？？？？？？？？？？？？？？？？
    # sub.set_name(parent_obj, getattr(child_obj, f"store_name_{childmedia}"), childmedia, getattr(child_obj, "yomigana"), getattr(child_obj, "yomi_roma"),manual=True)

    parent_obj.update_name(getattr(child_obj, f"store_name_{childmedia}"), childmedia)  # 各メディア用名前
    # 親のを保持。なかったら入れる
    if (not parent_obj.yomigana and child_obj.yomigana):
        parent_obj.yomigana = child_obj.yomigana
        parent_obj.save()
    if (not parent_obj.yomi_roma and child_obj.yomi_roma):
        parent_obj.yomi_roma = child_obj.yomi_roma
        parent_obj.save()

    # カテゴリーーーーーーーーー
    if not getattr(parent_obj, "category1") and getattr(child_obj, "category1"):
        parent_obj.category1 = child_obj.category1
        parent_obj.save()
    if not getattr(parent_obj, "category2") and getattr(child_obj, "category2"):
        parent_obj.category2 = child_obj.category2
        parent_obj.save()
    if not getattr(parent_obj, "category3") and getattr(child_obj, "category3"):
        parent_obj.category3 = child_obj.category3
        parent_obj.save()

    # 電話ーーーーーーーーーー
    if not getattr(parent_obj, "phone_number") and getattr(child_obj, "phone_number"):
        parent_obj.phone_number = child_obj.phone_number
        parent_obj.save()

    # 住所ーーーーーーーーーー
    sub.set_address(parent_obj, getattr(child_obj, "address"), childmedia)
    # # ぐるなびか食べログのを入れる。googleの住所はできれば替えたい
    # if (childmedia == "gn" and getattr(child_obj, "address")) or (childmedia == "tb" and getattr(child_obj, "address")) or (not getattr(parent_obj, "address") and getattr(child_obj, "address")):
    #     parent_obj.address = child_obj.address
    #     parent_obj.save()

    # メディアデーターーーーーーーー
    parent_m_data_obj, _ = models.Media_data.objects.update_or_create(store=parent_obj, media_type=child_m_type_obj)  # media_dataなければ作る
    try:
        parent_m_data_obj.url = child_m_data_obj.url
        parent_m_data_obj.save()
    except Exception:
        pass
    try:
        parent_m_data_obj.rate = child_m_data_obj.rate
        parent_m_data_obj.save()
    except Exception:
        pass
    try:
        parent_m_data_obj.review_count = child_m_data_obj.review_count
        parent_m_data_obj.save()
    except Exception:
        pass
    try:
        parent_m_data_obj.collected = child_m_data_obj.collected
        parent_m_data_obj.save()
    except Exception:
        pass

    all_md = models.Media_data.objects.filter(store=parent_obj)
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
    parent_obj.total_rate = total_rate
    parent_obj.save()

    # 店ごとのtotal_review_count登録ーーーーー
    rev_cnt_list = [md.review_count for md in all_md if md.review_count]
    try:
        total_review_count = sum(rev_cnt_list)
    except ZeroDivisionError:
        total_review_count = 0
    parent_obj.total_review_count = total_review_count
    parent_obj.save()

    # レビューーーーーーーーーーーー
    if models.Review.objects.filter(media=parent_m_data_obj).exists():
        models.Review.objects.filter(media=parent_m_data_obj).delete()
    bulk_rev_list = []
    already = []
    for o in child_r_objs:
        if o.content in already:
            continue
        try:
            title = o.title
        except Exception:
            title = None
        try:
            review_date = o.review_date
        except Exception:
            review_date = None
        try:
            log_num_byTabelog = o.log_num_byTabelog
        except Exception:
            log_num_byTabelog = None
        try:
            review_point = o.review_point
        except Exception:
            review_point = None
        r_obj = models.Review(
            media=parent_m_data_obj,
            content=o.content,
            title=title,
            review_date=review_date,
            log_num_byTabelog=log_num_byTabelog,
            review_point=review_point,
        )
        bulk_rev_list.append(r_obj)
        already.append(o.content)
        # r_obj, _ = models.Review.objects.update_or_create(
        #     media=parent_m_data_obj, content=o.content
        # )
        # r_obj.save()
    models.Review.objects.bulk_create(bulk_rev_list)

    return child_obj, childmedia, childname, parent_obj, child_m_data_obj


driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
def dupliNameToClip(d_name_len):
    while True:
        parent, child = "", ""
        print(f'あと{d_name_len}')
        d_name_len -= 1
        d_names = next(dupli_name_iter)
        if len(d_names) >= 3:
            for n in d_names:
                print(n + "\n")
            print('注※ 候補が3つ以上です')
            return d_name_len, parent, child
        print(f"1:{d_names[0]}\n2:{d_names[1]}")
        d_stores = models.Store.objects.filter(store_name__in=d_names, area__area_name=area)
        if len(d_stores) <= 1:
            print('たぶん消してます')
            # return d_name_len, parent, child
            continue
        st1, st2 = d_stores
        d_name_lists = []
        d_name_lists.append([st1.store_name.replace(' ','').replace('　',''), st2.store_name.replace(' ','').replace('　','')])
        if st1.yomigana and st2.yomigana:
            converted1 = kakasi.convert(st1.yomigana)
            yomi1 = "".join([s["hira"] for s in converted1])
            converted2 = kakasi.convert(st2.yomigana)
            yomi2 = "".join([s["hira"] for s in converted2])
            d_name_lists.append([yomi1, yomi2])
        if st1.yomi_roma and st2.yomi_roma:
            d_name_lists.append([st1.yomi_roma, st2.yomi_roma])

        match_list = []
        for d_name1, d_name2 in d_name_lists:
            d_name1 = d_name1.replace(area2[:-1],"").replace(area2_roma,"").replace(area2_hira,"")
            d_name2 = d_name2.replace(area2[:-1],"").replace(area2_roma,"").replace(area2_hira,"")
            match = SequenceMatcher(None, d_name1, d_name2).find_longest_match(0, len(d_name1), 0, len(d_name2))
            match_list.append(d_name1[match.a: match.a + match.size])
        # print(match_list)
        # pyperclip.copy(max(match_list, key=len))

        # driver.find_element_by_id('input-27').send_keys(area1 + " " + area2  + Keys.ENTER)
        driver.find_element_by_id('input-18').clear()
        driver.find_element_by_id('input-18').send_keys(max(match_list, key=len)  + Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])

        submit = input("parent is.. 1 or 2 or 0: ")
        if submit == "1":
            parent, child = d_names[0], d_names[1]
        elif submit == "2":
            parent, child = d_names[1], d_names[0]
            
        return d_name_len, parent, child


area = "埼玉県 大宮"
area = "埼玉県 浦和"
area = "千葉県 柏市"
area = "千葉県 習志野市"
area = "東京都 新宿駅"
area = "東京都 六本木駅"
area = "東京都 銀座駅"
area = "東京都 青山一丁目駅"
area = "東京都 国分寺駅"
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname="大衆馬肉酒場 Popular horse meat bar Jockey", childmedia="uber", parentname="大衆馬肉酒場 ジョッキー", area=area)
child_obj.delete()

# 単店 google md消す
models.Media_data.objects.get(store=parent_obj, media_type__media_type="google").delete()
models.Media_data.objects.get(store=st, media_type__media_type="google").delete()

st: models.Store = models.Store.objects.get(store_name="巴裡 小川軒 サロン・ド・テ 新橋店", area__area_name=area)
st.yomigana = "とんぶざ"
st.yomi_roma = "tonbuza"
st.address = "東京都港区麻布十番1-8-5 パステル麻布3F"
st.store_name_google = None
st.save()

if input('media_dataとstore_name_by_media消す？y/n: ') == "y":
    child_m_data_obj.delete()
    setattr(child_obj, f"store_name_{childmedia}", None)
    child_obj.save()

if input('store消す？y/n: ') == "y":
    child_obj.delete()
    # 食べログの場合。子を消してから本名乗っ取る
    if childmedia == "tb":
        print(f"確認：\n{parent_obj.store_name}\n{parent_obj.yomigana}\n{parent_obj.yomi_roma}")
        parent_obj.update_name(childname)

        parent_obj.yomigana = child_obj.yomigana
        parent_obj.yomi_roma = child_obj.yomi_roma
        parent_obj.save()

# 消すーーーーーーーーーー
models.Store.objects.get(store_name="蘭", area__area_name=area).delete()
# models.Store.objects.filter(store_name__startswith="ほっともっと").delete()
models.Store.objects.filter(area__area_name="東京都 町田駅").delete()
models.Area.objects.get(area_name="東京都 町田駅").delete()

# googleのmedia_data消す
ga = models.Media_data.objects.filter(store__area__area_name="千葉県 船橋市", media_type__media_type="hp")
ga.delete()

# md 1種類消す
mt = "google"
st = models.Store.objects.get(store_name="やまちゃん", area__area_name=area)
setattr(st, f"store_name_{mt}", None)
st.save()
models.Media_data.objects.get(store=st, media_type__media_type=mt).delete()


# かぶり店名サーチーーーーーーーーーーー
filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/dupli*")
file = filepaths[0]
area1, area2 = file.split('_')[1], file.split('_')[2]
area = area1 + " " + area2
print(f"{file}")
with open(file) as f:
    data = f.read()
name_list: list = data.strip().replace("dupliエラー:", "").split('\n\n')
d_name_len = len(name_list)
dupli_name_iter = (n.strip().split("\n") for n in name_list)
kakasi = pykakasi.kakasi()
converted = kakasi.convert(area2[:-1])
area2_hira = "".join([s["hira"] for s in converted])
area2_roma = "".join([s["hepburn"] for s in converted])
print(file)
driver.get("https://restaurary.com/")
def bundle_CI(child_mt:str): # まとめて用
    child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname=child, childmedia=child_mt, parentname=parent, area=area)
    child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname=child, childmedia="google", parentname=parent, area=area)
    child_obj.delete()
    return child_obj, childmedia, childname, parent_obj, child_m_data_obj

d_name_len, parent, child = dupliNameToClip(d_name_len)

child_obj, childmedia, childname, parent_obj, child_m_data_obj = bundle_CI(child_mt="gn")
child_obj, childmedia, childname, parent_obj, child_m_data_obj = bundle_CI(child_mt="tb")

parent_obj.update_name(childname) # 名前変更
sub.deleteAndAddClosedname(childname, area1, area2) # 削除
sub.deleteAndAddClosedname("春日亭", area1, area2) # 削除
send2trash(file)

# ひとつずつ用
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname=child, childmedia="gn", parentname=parent, area=area)
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname=child, childmedia="tb", parentname=parent, area=area)
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname=child, childmedia="google", parentname=parent, area=area)
child_obj.delete()
# ーーーーーーーーーーーーーーかぶり店名サーチ


# storeを area mediatypeで消すーーー
area = "習志野市"
mediatype = "tb"
sts = models.Store.objects.filter(area__area_name__icontains=area)
sts = [st for st in sts if getattr(st, f"store_name_{mediatype}")]
le = len(sts)
for st in sts:
    print(le)
    st.delete()
    le -= 1


# よみがな追加ーーーーーーー
def insert_yomigana():
    import re
    import pykakasi
    kakasi = pykakasi.kakasi()
    le = models.Store.objects.all().count()
    for st in models.Store.objects.all():
        print(le)
        yomi = st.yomigana
        if not yomi:
            yomi = "a"
        if re.fullmatch("[a-zA-Z0-9]+", yomi):
            print(st.store_name)
            print(f'よみ {yomi}')
            conv = kakasi.convert(st.store_name)
            name_hira = "".join([s["hira"] for s in conv])
            st.yomigana = name_hira[:99]
            st.save()
        if not st.yomi_roma:
            name_roma = "".join([s["hepburn"] for s in conv])
            st.yomi_roma = name_roma[:99]
            st.save()
        le -= 1


# エリアごとmedia_type別media_data数
def show_madiadata_count():
    # area = "千葉県 習志野市"
    area = "千葉県 木更津市"
    # area = "千葉県 館山市"
    # area = "千葉県 松戸市"
    # area = "東京都 中目黒"
    # area = "東京都 新宿"
    # area = "埼玉県 さいたま市"

    import collections

    now = datetime.datetime.now()
    li = []
    mdobjs = models.Media_data.objects.filter(store__area__area_name=area)
    le = mdobjs.count()
    for md in mdobjs:
        print(f"あと{le}")
        li.append(md.media_type.__str__())
        le -= 1
    print(collections.Counter(li))
    time = datetime.datetime.now() - now
    print(time)

    # カテゴリ
    storeobjs = models.Store.objects.filter(area__area_name=area)
    category_li = []
    le = storeobjs.count()
    for storeobj in storeobjs:
        print(f"あと{le}")
        category_li.append(storeobj.category1)
        category_li.append(storeobj.category2)
        category_li.append(storeobj.category3)
        le -= 1
    print(collections.Counter(category_li))


# 店ごとのtotal_rate登録ーーーーー----------------
store_objs = models.Store.objects.all()
# store_objs = models.Store.objects.filter(area__area_name="千葉県 船橋市")
le = store_objs.count()
for st in store_objs:
    print(le)
    # all_md = models.Media_data.objects.filter(store=st, media_type__media_type__in=["gn", "google", "tb", "uber"])
    all_md = models.Media_data.objects.filter(store=st)

    total_rate = sub.setTotalRateForStore(all_md)

    st.total_rate = total_rate
    st.save()
    le -= 1


# json fileの一部抜き出し
def jjjj():
    end_page = 14
    import datetime
    import json

    def date_trans_json(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d')
    file = "/Users/yutakakudo/Google ドライブ/colab/json/使用済/google_千葉県_松戸市_3から18_2021-07-09_0141.json"
    area1 = file.split('_')[1]
    area2 = file.split('_')[2]
    print(f"{area1} {area2}")
    media_type = file.split('_')[0].split('/')[-1]
    print(f"media_type {media_type}")
    start_page = file.split('_')[3].split('から')[0]
    # page_num = file.split('_')[3].split('から')[1]
    print("start_page", start_page)
    n = datetime.datetime.now()

    with open(file) as f:
        jfile = json.load(f)
    len(jj)

    jj = jfile[:(end_page-2)*20]
    jfile[:end_page*20]

    with open(f"/Users/yutakakudo/Google ドライブ/colab/json/{media_type}_{area1}_{area2}_新{start_page}から{end_page}_{n.strftime('%Y-%m-%d_%H%M')}.json", "w") as f:
        json.dump(jj, f, indent=4, default=date_trans_json)


def collectStoreOtherThanThaaaaaaaaaat():
    from site_packages.my_module import collectStoreOtherThanThat
    area1 = "千葉県"
    area2 = "船橋市"
    # area2 = "市川市"

    area_name = area1 + " " + area2
    media = "google"

    to_collect = collectStoreOtherThanThat(area_name, media)
    n = datetime.now()
    with open(f"/Users/yutakakudo/Google ドライブ/colab/json/refill_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
        for line in to_collect:
            f.write(f"{line}\n")


# UBER ONLYを探す
stores = models.Store.objects.filter(area__area_name=area)
leng = len(stores)
lilli = []
for enum, st in enumerate(stores):
    print(leng - enum)
    if [md.media_type.media_type for md in models.Media_data.objects.filter(store=st)] == ["uber"]:
        lilli.append(st.store_name)
print(lilli)
models.Store.objects.filter(store_name__in=lilli).delete()
