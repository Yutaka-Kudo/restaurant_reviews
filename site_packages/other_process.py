
# media_dataのないstoreを掃除ーーーーーーーーー
# area_obj = models.Area.objects.get(area_name="千葉県 市川市")


from scrape import models
from decimal import Decimal

def clean_store_obj(area_obj):
    store_objs = models.Store.objects.all()
    # store_objs = models.Store.objects.filter(area__area_name="千葉県 銚子市")
    count = len(store_objs)
    destroy = []
    for s in store_objs:
        if len(models.Media_data.objects.filter(store=s)) == 0:
            destroy.append(s)
            s.delete()
        print(f"count あと {count}")
        count -= 1

    # 確認のみ
    from pprint import pprint as pp
    be_deleted = [[s.store_name, s.area.__str__()] for s in store_objs if len(models.Media_data.objects.filter(store=s)) == 0]
    pp(be_deleted)


# 重複を統合ーーーーーーーーーー
def conflict_integration(childname, childmedia, parentname, area=""):
    from scrape import models

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
    # parent_obj.update_name(target_store_name_by_media, childmedia)  # 各メディア用名前
    parent_obj.update_name(getattr(child_obj, f"store_name_{childmedia}"), childmedia)  # 各メディア用名前
    # ぐるなび読み仮名が入ってたら問答無用で入れ替え
    if (childmedia == "gn" and getattr(child_obj, "yomigana")) or (not getattr(parent_obj, "yomigana") and getattr(child_obj, "yomigana")):
        parent_obj.yomigana = child_obj.yomigana
        parent_obj.save()
    if (childmedia == "gn" and getattr(child_obj, "yomi_roma")) or (not getattr(parent_obj, "yomi_roma") and getattr(child_obj, "yomi_roma")):
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
    # ぐるなびか食べログのを入れる。googleの住所はできれば替えたい
    if (childmedia == "gn" and getattr(child_obj, "address")) or (childmedia == "tb" and getattr(child_obj, "address")) or (not getattr(parent_obj, "address") and getattr(child_obj, "address")):
        parent_obj.address = child_obj.address
        parent_obj.save()

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
            r_obj.save()
        except Exception:
            pass
        try:
            r_obj.review_date = o.review_date
            r_obj.save()
        except Exception:
            pass
        try:
            r_obj.log_num_byTabelog = o.log_num_byTabelog
            r_obj.save()
        except Exception:
            pass
        try:
            r_obj.review_point = o.review_point
            r_obj.save()
        except Exception:
            pass
    return child_obj, childmedia, childname, parent_obj, child_m_data_obj


area = "千葉県 船橋市"
area = "千葉県 市川市"
area = "千葉県 千葉市"
# area = "千葉県 柏市"
area = "東京都 麻布"
area = "東京都 青山"
area = "大阪府 梅田"
area = "大阪府 天王寺"
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname="築地銀だこ", childmedia="google", parentname="築地銀だこハイボール酒場 サンモール中野店", area=area)
child_obj, childmedia, childname, parent_obj, child_m_data_obj = conflict_integration(childname="日本酒バル 富成喜笑店", childmedia="gn", parentname="日本酒バル じゃのめん", area="")
child_obj.delete()


st = models.Store.objects.filter(store_name="日本酒バル じゃのめん")[0]
# me = models.Media_data.objects.filter(store=st)[0]

if input('media_dataとstore_name_by_media消す？y/n: ') == "y":
    child_m_data_obj.delete()
    setattr(child_obj, f"store_name_{childmedia}", None)
    child_obj.save()

if input('store消す？y/n: ') == "y":
    child_obj.delete()
    # 食べログの場合。子を消してから本名乗っ取る
    if childmedia == "tb":
        parent_obj.update_name(childname)

# 消すーーーーーーーーーー
ta = models.Store.objects.get(store_name="レストラン", area__area_name__icontains="六本木")
ta = models.Store.objects.get(store_name="ファミリーマート お台場海浜公園店")
ta.delete()
models.Store.objects.get(store_name="厨房機器 店舗用品販売 テンポス柏店").delete()
models.Store.objects.filter(store_name__startswith="TOHOシネマズ").delete()
# , area__area_name__icontains="銀座")
# ta.area

# models.Media_data.objects.filter(store=5148)

# area mediatypeで消すーーー
area = "中野"
mediatype = "tb"
na = models.Store.objects.filter(area__area_name__icontains=area)
na = [o for o in na if getattr(o, f"store_name_{mediatype}")]
le = len(na)
for i in na:
    print(le)
    i.delete()
    le -= 1

# よみがな追加ーーーーーーー


def insert_yomigana():
    import re
    import pykakasi
    kakasi = pykakasi.kakasi()
    le = len(models.Store.objects.all())
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
    # area = "千葉県 船橋市"
    # area = "千葉県 千葉市"
    # area = "千葉県 館山"
    area = "千葉県 松戸市"
    # area = "東京都 中目黒"
    # area = "東京都 新宿"
    # area = "埼玉県 さいたま市"

    import collections

    areaobj = models.Area.objects.get(area_name=area)
    storeobjs = models.Store.objects.filter(area=areaobj)

    li = []
    le = len(storeobjs)
    for storeobj in storeobjs:
        print(f"あと{le}")
        mdobjs = models.Media_data.objects.filter(store=storeobj)
        for md in mdobjs:
            li.append(md.media_type.__str__())
        le -= 1
    print(collections.Counter(li))


# 店ごとのtotal_rate登録ーーーーー
def set_total_rate():
    from decimal import Decimal
    store_objs = models.Store.objects.all()
    # store_objs = models.Store.objects.filter(area__area_name="千葉県 船橋市")
    le = len(store_objs)
    for st in store_objs:
        print(le)
        all_md = models.Media_data.objects.filter(store=st, media_type__media_type__in=["gn", "google", "tb", "uber"])

        rate_list, total_review_count = [], []

        for md in all_md:
            if md.media_type.__str__() == "tb":  # 食べログ補正
                rate = md.rate + ((md.rate - Decimal("2.5")) * Decimal(".6"))
                # 計算用
                # a = 4
                # (a - 2.5)*.6 + a
                # a*1.2
            else:
                rate = md.rate
            if md.review_count:
                rate_list.append(rate * md.review_count)
                total_review_count.append(md.review_count)

        # rate_list = [(md.rate * md.review_count) for md in all_md if md.review_count]
        # total_review_count = [md.review_count for md in all_md if md.review_count]

        try:
            total_rate = sum(rate_list) / sum(total_review_count)
        except ZeroDivisionError:
            total_rate = 0
        st.total_rate = total_rate
        st.save()
        le -= 1
