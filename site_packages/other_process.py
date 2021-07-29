
from scrape import models
from site_packages import sub
from decimal import Decimal
import datetime

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
    # sub.name_set(parent_obj, getattr(child_obj, f"store_name_{childmedia}"), childmedia, getattr(child_obj, "yomigana"), getattr(child_obj, "yomi_roma"),manual=True)

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
    sub.address_set(parent_obj, getattr(child_obj, "address"), childmedia)
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
    for o in child_r_objs:
        r_obj, _ = models.Review.objects.update_or_create(
            media=parent_m_data_obj, content=o.content
        )
        try:
            r_obj.title = o.title
        except Exception:
            pass
        try:
            r_obj.review_date = o.review_date
        except Exception:
            pass
        try:
            r_obj.log_num_byTabelog = o.log_num_byTabelog
        except Exception:
            pass
        try:
            r_obj.review_point = o.review_point
        except Exception:
            pass

        r_obj.save()
    return child_obj, childmedia, childname, parent_obj, child_m_data_obj


area = "埼玉県 越谷市"
area = "埼玉県 熊谷市"
area = "埼玉県 大宮"
area = "埼玉県 浦和"
area = "千葉県 柏市"
area = "千葉県 習志野市"
area = "千葉県 市川市"
area = "千葉県 船橋市"
area = "千葉県 木更津市"
area = "東京都 新宿"
area = "東京都 青山"
area = "大阪府 梅田"
area = "大阪府 天王寺"
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname="築地銀だこ", childmedia="google", parentname="", area=area)
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname="ニムタ 南浦和店", childmedia="tb", parentname="ニムタ 南浦和1号店", area=area)
child_obj.delete()


st = models.Store.objects.get(store_name="Egg Egg キッチン レイクタウン店")
st.yomigana = "ことぶきやほんてん"
st.yomi_roma = "kotobukiyahonten"
st.save()
me = models.Media_data.objects.filter(store=st)[0]
me.__dict__
me.delete()

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

        parent_obj.yomi_roma = childname
        parent_obj.save()

# 消すーーーーーーーーーー
ta = models.Store.objects.get(store_name="レストラン", area__area_name__icontains="六本木")
ta = models.Store.objects.get(store_name="旬菜")
ta.delete()
models.Store.objects.get(store_name="蘭茶", area__area_name=area).delete()
# models.Store.objects.filter(store_name__startswith="ほっともっと").delete()
# models.Store.objects.filter(area__area_name="埼玉県 越谷市").delete()

# googleのmedia_data消す
ga = models.Media_data.objects.filter(store__area__area_name="千葉県 船橋市", media_type__media_type="hp")
ga.delete()

# models.Media_data.objects.filter(store=5148)


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
