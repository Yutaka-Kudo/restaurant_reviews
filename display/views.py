# import json
# from django.http import JsonResponse
# from datetime import datetime
# from scrape import models
# from scrape.scrape_tb import scrape_tb
# from site_packages.my_module import Compare_storeName

# from django.shortcuts import render, redirect
# from django.db.models import Q

# from pprint import pprint as pp
# from devtools import debug


# def admin(request):
#     return redirect('/admin/')


# def index(request):

#     context = {}

#     return render(request, "display/index.html", context)


# def store_list(request):
#     area_q: str = request.GET.get('area')
#     store_q: str = request.GET.get('store')

#     context = {
#         "area": area_q,
#         "store_q": store_q,
#     }
#     return render(request, "display/store_list.html", context)


# # デバッグ用
# # def scra(request):
# #     scrape_tb("千葉県","船橋市")
# #     return redirect('/')




# def show_details(request, area_q, store_q):
#     area_obj = models.Area.objects.get(area_name__icontains=area_q)

#     store_objs_in_area = models.Store.objects.filter(area=area_obj)
#     # 検索ーーーーーーー
#     if store_q:
#         match_store_obj_list = [s for s in store_objs_in_area if store_q in s.store_name]
#         compare = Compare_storeName()
#         store_kouho_dict = compare.search_store_name(store_q, store_objs_in_area, min_ratio=0.2)  # 一致率0.2以上を集める
#         sorted_store_obj_list = sorted(store_kouho_dict.items(), key=lambda x: x[1]["ratio"], reverse=True)  # ratio順にソート
#         sorted_store_obj_list = [o[0] for o in sorted_store_obj_list]  # objだけとる
#         sorted_store_obj_list = match_store_obj_list + sorted_store_obj_list
#         sorted_store_obj_list = sorted(set(sorted_store_obj_list), key=sorted_store_obj_list.index)  # 順番変わらないようにset
#     else:
#         sorted_store_obj_list = store_objs_in_area.order_by("store_name")

#     media_type_objs = models.Media_type.objects.all()

#     stores_data_list = []
#     for store_obj in sorted_store_obj_list:
#         store_dict = {"store_name": store_obj.store_name}
#         store_dict["media_type"] = list(media_type_objs.values())

#         rate_list = []
#         review_count_list = []

#         for i, media_type_obj in enumerate(media_type_objs):
#             try:
#                 media_data_objs = models.Media_data.objects.filter(store=store_obj, media_type=media_type_obj)  # getで取りたいが、.values()が使えなくなる
#                 media_data = list(media_data_objs.values())[0]
#             except Exception as e:
#                 # print(type(e), e, media_type_obj, 'media_data_objがありません。')
#                 store_dict["media_type"][i]["media_data"] = {}
#             else:
#                 rate_list.append(media_data["rate"])
#                 review_count_list.append(media_data["review_count"])
#                 store_dict["media_type"][i]["media_data"] = media_data
#                 # 星用点数ーーー
#                 store_dict["media_type"][i]["media_data"]["rate_for_star"] = round(media_data["rate"],1)

#                 review_objs = models.Review.objects.filter(media=media_data_objs[0]).order_by('-review_date')
#                 store_dict["media_type"][i]["media_data"]["review"] = list(review_objs.values())
#                 # 星用点数ーーー
#                 for ii, review in enumerate(store_dict["media_type"][i]["media_data"]["review"]):
#                     try:
#                         store_dict["media_type"][i]["media_data"]["review"][ii]["review_point_for_star"] = round(review["review_point"], 1)
#                     except TypeError: # noneがある
#                         store_dict["media_type"][i]["media_data"]["review"][ii]["review_point_for_star"] = "0.0"

#         registed_media_type = []
#         for i in store_dict["media_type"]:
#             try:
#                 if i["media_data"]:
#                     registed_media_type.append(i["media_type"])
#             except Exception:
#                 pass
        
#         store_dict["registed_media_type"] = registed_media_type
#         store_dict["only_uber_flg"] = True if registed_media_type == ["uber"] else False

#         # 総合レートーーーーーーーー
#         rate_list = [r for r in rate_list if r]  # 0, noneを除去
#         try:
#             store_dict["total_rate"] = round(sum(rate_list) / len(rate_list), 2)
#             store_dict["total_rate_for_star"] = round(sum(rate_list) / len(rate_list), 1)

#         except Exception:  # 0, noneを除去して無くなっちゃったものに対して。
#             store_dict["total_rate"] = 0
#             store_dict["total_rate_for_star"] = 0

#         # 総合レビュー数ーーーーーーー
#         review_count_list = [r for r in review_count_list if r]  # 0, noneを除去
#         try:
#             store_dict["total_review_count"] = sum(review_count_list)
#         except Exception:  # 0, noneを除去して無くなっちゃったものに対して。
#             store_dict["total_review_count"] = 0

#         stores_data_list.append(store_dict)
#     # debug(stores_data_list)
#     return JsonResponse(stores_data_list, safe=False)
