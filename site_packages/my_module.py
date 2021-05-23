# import datetime
# import os
# from scrape import models
# from devtools import debug
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# from janome.tokenfilter import *
# from janome.charfilter import *
# from janome.analyzer import Analyzer
# from janome.tokenizer import Tokenizer
# import difflib
# import re


# def capture(driver):
#     n = datetime.datetime.now()
#     FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"static/images/screen{n.date()}{n.hour}{n.minute}.png")  # なんでhourとminuteで分けてるんだっけ？
#     w = driver.execute_script('return document.body.scrollWidth;')
#     h = driver.execute_script('return document.body.scrollHeight;')
#     driver.set_window_size(w, h)
#     driver.save_screenshot(FILENAME)


# class Wait_located:
#     def __init__(self, driver):
#         self.driver = driver

#     def wait_lacated_id(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, value)))

#     def wait_lacated_xpath(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, value)))

#     def wait_lacated_link_text(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, value)))

#     def wait_lacated_partial_link_text(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, value)))

#     def wait_lacated_name(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, value)))

#     def wait_lacated_tag_name(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, value)))

#     def wait_lacated_class_name(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, value)))

#     def wait_lacated_css_selector(self, value: str):
#         return WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, value)))


# class Compare_storeName:
#     def __init__(self):
#         char_filters = [UnicodeNormalizeCharFilter()]  # 半角 → 全角 等
#         token_filters = [LowerCaseFilter(), ExtractAttributeFilter('surface')]  # 小文字に ＆ 抽出する属性
#         self.a = Analyzer(char_filters=char_filters, token_filters=token_filters)

#     def search_store_name(self, store_name: str, querysets, ignore_list: list = None, media: str = "", min_ratio: float = 0.6):

#         def remove_unnecessary_word(store_name: str, ignore_list: list) -> str:
#             for s in re.findall(r"【.*?】", store_name):  # 【...】を除去
#                 store_name = store_name.replace(s, '')
#             for s in re.findall(r"-.*?-", store_name):  # 【...】を除去
#                 store_name = store_name.replace(s, '')

#             analyzed_name: list = list(self.a.analyze(store_name))
#             for w in ignore_list:
#                 # analyzed_name = [s for s in analyzed_name if s != w]
#                 # return ''.join(analyzed_name)
#                 analyzed_name = ''.join(analyzed_name).replace(w, '')
#             return analyzed_name

#         if ignore_list is None:
#             ignore_list = []

#         clean_name = remove_unnecessary_word(store_name, ignore_list)
#         debug(clean_name)
#         debug(media)

#         # models.Store.objects.filter(area=area_obj)
#         # for i in models.Store.objects.filter(area=area_obj):
#         #     print(i.store_name)

#         store_kouho_dict = {}

#         # store_kouho_list, ratio_list = [], []
#         for obj in querysets:
#             try:
#                 if media == "":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name, ignore_list)
#                 elif media == "gn":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_gn, ignore_list)
#                 elif media == "hp":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_hp, ignore_list)
#                 elif media == "tb":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_tb, ignore_list)
#                 elif media == "retty":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_retty, ignore_list)
#                 elif media == "demaekan":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_demaekan, ignore_list)
#                 elif media == "uber":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_uber, ignore_list)
#                 elif media == "google":
#                     clean_name_in_db = remove_unnecessary_word(obj.store_name_google, ignore_list)
#                 else:
#                     raise Exception('media が間違っています。')
#             except Exception:  # 新しいメディアからの初期登録時。上の処理はデータがないとバグるため
#                 clean_name_in_db = " "

#             ratio = difflib.SequenceMatcher(lambda x: x in [" ", "-"], clean_name, clean_name_in_db).ratio()  # 類似度

#             if ratio > min_ratio:
#                 # store_kouho_list.append(obj)
#                 # ratio_list.append(ratio)
#                 # debug(clean_name_in_db, ratio)
#                 store_kouho_dict.update({obj: {"ratio": ratio, "clean_name": clean_name, "clean_name_in_db": clean_name_in_db}})

#         # return dict(zip(store_kouho_list, ratio_list))
#         return store_kouho_dict


# # 店名でstore_object取得  1番近いものを探すーーーー
# def store_model_process(area_obj: models.Area, media_type: str, store_name: str, ignore_list: list, phone: str = ""):
#     _atode_flg = False
#     _atode_dict = {}
#     _created_list = []

#     store_objs = models.Store.objects.filter(area=area_obj)

#     compare = Compare_storeName()

#     print("----------------\n" + store_name)
#     print('first_attack!')
#     store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media=media_type, min_ratio=0.7)  # mediaごとの名前で照会。同じメディアでも名前が微妙に変わることがあるので完全一致で探さない。
#     if store_kouho_dict:
#         # debug(store_kouho_dict)
#         store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得

#         store_obj.update_name(store_name, media_type)
#         if media_type == "tb":
#             store_obj.update_name(store_name)
#         print('get store_obj!!')
    
#     else:
#         print('second_attack!')
#         store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=0.8)  # 今度はDB内の名前で照会
#         if store_kouho_dict:
#             debug(store_kouho_dict)
#             store_obj, _ = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得
#             store_obj.update_name(store_name, media_type)
#             if media_type == "tb":
#                 store_obj.update_name(store_name)
#             print('get store_obj and update!!')
#         else:
#             print('third_attack!')
#             store_kouho_dict = compare.search_store_name(store_name, store_objs, ignore_list, media='', min_ratio=0.4)  # 今度はDB内の名前で照会
#             if store_kouho_dict:
#                 debug(store_kouho_dict)
#                 store_obj, sub_name_dict = max(store_kouho_dict.items(), key=lambda x: x[1]["ratio"])  # 最大値のkeyを取得
#                 debug(store_obj.store_name)

#                 # あるか無いか微妙なラインなのでatodeシリーズにまとめで確認
#                 print('atode...')
#                 _atode_flg = True
#                 _atode_dict["store_name_db"] = store_obj.store_name
#                 _atode_dict["store_name_site"] = store_name
#                 _atode_dict["clean_name"] = sub_name_dict["clean_name"]
#                 _atode_dict["clean_name_in_db"] = sub_name_dict["clean_name_in_db"]
#                 if phone:
#                     _atode_dict["phone"] = phone

#             else:
#                 store_obj, _ = models.Store.objects.get_or_create(store_name=store_name, area=area_obj)  # (注)store_name_tb のところは各媒体で変える
#                 store_obj.update_name(store_name, media_type)
#                 if phone:
#                     store_obj.phone_number = phone
#                     store_obj.save()

#                 _created_list.append(store_name)
#                 print('create store_obj!!')

#     return store_obj, _atode_flg, _atode_dict, _created_list


# def atode_process(atode_list: list, media_type: str, media_type_obj: models.Media_type, area_obj: models.Area):
#     _created_list = []
#     not_adopted_list = []

#     debug(atode_list)
#     for i, store in enumerate(atode_list):
#         print(f'この名前: {store["store_name_site"]}  \nDBの名前: {store["store_name_db"]}\nclean   : {store["clean_name"]}\nclean_db: {store["clean_name_in_db"]}')

#         def submit_update():
#             submit = input('この名前ですか？y / N： ').lower()
#             if submit == "y":
#                 store_obj = models.Store.objects.get(store_name=store["store_name_db"], area=area_obj)
#                 store_obj.update_name(store["store_name_site"], media_type)
#                 if media_type == "tb":  # 食べログの名前を正式名称にする
#                     store_obj.update_name(store["store_name_site"])
#                 try:
#                     store_obj.phone_number = store["phone"]
#                     store_obj.save()
#                 except KeyError:
#                     pass

#                 media_obj, _ = models.Media_data.objects.update_or_create(
#                     store=store_obj, media_type=media_type_obj,
#                     defaults={
#                         "rate": store["rate"],
#                     }
#                 )
#                 try:
#                     media_obj.url = store["store_url"]
#                     media_obj.save()
#                 except KeyError:
#                     pass
#                 try:
#                     media_obj.review_count = store["review_count"]
#                     media_obj.save()
#                 except KeyError:
#                     pass

#                 if media_type == "tb":
#                     try:
#                         for review in store["review"]:
#                             models.Review.objects.update_or_create(
#                                 media=media_obj, title=review["title"], defaults={
#                                     "content": review["content"],
#                                     "review_date": review["date"],
#                                     "log_num_byTabelog": review["log_num"],
#                                     "review_point": review["review_point"],
#                                 }
#                             )
#                         # review_count = len(models.Review.objects.filter(media=media_obj))
#                         # media_obj.review_count = review_count
#                         # media_obj.save()
#                     except Exception as e:
#                         print(type(e), e)
#                 elif media_type == "google":
#                     try:
#                         for review in store["review"]:
#                             models.Review.objects.update_or_create(
#                                 media=media_obj, content=review["content"], defaults={
#                                     "review_date": review["date"],
#                                     "review_point": review["review_point"],
#                                 }
#                             )
#                         # review_count = len(models.Review.objects.filter(media=media_obj))
#                         # media_obj.review_count = review_count
#                         # media_obj.save()
#                     except Exception as e:
#                         print(type(e), e)
#                 elif media_type == "gn":
#                     try:
#                         for review in store["review"]:
#                             models.Review.objects.update_or_create(
#                                 media=media_obj, title=review["title"], defaults={
#                                     "content": review["content"],
#                                     "review_date": review["date"],
#                                     "review_point": review["review_point"],
#                                 }
#                             )
#                     except Exception as e:
#                         print(type(e), e)
#                 elif media_type == "hp":
#                     try:
#                         for review in store["review"]:
#                             models.Review.objects.update_or_create(
#                                 media=media_obj, content=review["content"], defaults={
#                                     "review_date": review["date"],
#                                 }
#                             )
#                         # review_count = len(models.Review.objects.filter(media=media_obj))
#                         # media_obj.review_count = review_count
#                         # media_obj.save()
#                     except Exception as e:
#                         print(type(e), e)
#                 elif media_type == "demaekan":
#                     pass
#                 elif media_type == "retty":
#                     pass

#                 print('update OK!')

#             elif submit == "n":
#                 def submit_regist():
#                     regist = input('新規登録しますか？y / N: ').lower()
#                     if regist == "y":
#                         store_obj, _ = models.Store.objects.get_or_create(
#                             store_name=store["store_name_site"],
#                             area=area_obj,
#                         )
#                         store_obj.update_name(store["store_name_site"], media_type)
#                         try:
#                             store_obj.phone_number = store["phone"]
#                             store_obj.save()
#                         except KeyError:
#                             pass
#                         media_obj, _ = models.Media_data.objects.get_or_create(
#                             store=store_obj,
#                             media_type=media_type_obj,
#                         )
#                         try:
#                             media_obj.rate = store["rate"]
#                             media_obj.save()
#                         except Exception:
#                             pass
#                         try:
#                             media_obj.url = store["store_url"]
#                             media_obj.save()
#                         except Exception:
#                             pass
#                         try:
#                             media_obj.review_count = store["review_count"]
#                             media_obj.save()
#                         except Exception:
#                             pass

#                         # レビューーーーーーーーーーー
#                         if media_type == "tb":
#                             try:
#                                 for review in store["review"]:
#                                     models.Review.objects.create(
#                                         media=media_obj,
#                                         title=review["title"],
#                                         content=review["content"],
#                                         review_date=review["date"],
#                                         log_num_byTabelog=review["log_num"],
#                                         review_point=review["review_point"],
#                                     )
#                                 # review_count = len(models.Review.objects.filter(media=media_obj))
#                                 # media_obj.review_count = review_count
#                                 # media_obj.save()
#                             except Exception as e:
#                                 print(type(e), e)
#                         elif media_type == "google":
#                             try:
#                                 for review in store["review"]:
#                                     models.Review.objects.create(
#                                         media=media_obj,
#                                         content=review["content"],
#                                         review_date=review["date"],
#                                         review_point=review["review_point"],
#                                     )
#                             except Exception as e:
#                                 print(type(e), e)
#                         elif media_type == "gn":
#                             try:
#                                 for review in store["review"]:
#                                     models.Review.objects.create(
#                                         media=media_obj,
#                                         title=review["title"],
#                                         content=review["content"],
#                                         review_date=review["date"],
#                                         review_point=review["review_point"],
#                                     )
#                             except Exception as e:
#                                 print(type(e), e)
#                         elif media_type == "hp":
#                             try:
#                                 for review in store["review"]:
#                                     models.Review.objects.create(
#                                         media=media_obj,
#                                         content=review["content"],
#                                         review_date=review["date"],
#                                     )
#                             except Exception as e:
#                                 print(type(e), e)
#                             pass
#                         elif media_type == "retty":
#                             pass
#                         elif media_type == "demaekan":
#                             pass

#                         print('regist OK!')
#                         _created_list.append(store["store_name_site"])

#                     elif regist == "n":  # ゴミ箱いき
#                         not_adopted_list.append(store["store_name_site"])
#                         print('move not_adopted_list')
#                     else:  # やり直し
#                         return submit_regist()
#                 submit_regist()

#             else:
#                 return submit_update()
#         submit_update()
#         print(len(atode_list)-i)

#     return _created_list, not_adopted_list


# # UNIQUE constraint failed: scrape_store.store_name, scrape_store.area_id

# # 重複を統合ーーーーーーーーーー
# def conflict_integration():  # 名前とメディアタイプ変えるだけ
#     store: str = "肉と日本酒 ときどきワイン 船橋ガーデン"  # 親
#     target_store: str = "船橋ガーデン 船橋駅前店"  # 子
#     target_media_type: str = "google"

#     target_store_obj = models.Store.objects.get(store_name=target_store)
#     target_m_type_obj = models.Media_type.objects.get(media_type=target_media_type)
#     target_m_data_obj = models.Media_data.objects.get(store=target_store_obj, media_type=target_m_type_obj)
#     target_r_objs = models.Review.objects.filter(media=target_m_data_obj)

#     # 入れる方
#     store_obj = models.Store.objects.get(store_name=store)
#     store_obj.update_name(target_store,target_media_type)
#     m_data_obj, _ = models.Media_data.objects.update_or_create(store=store_obj, media_type=target_m_type_obj)
#     try:
#         m_data_obj.url = target_m_data_obj.url
#         m_data_obj.save()
#     except Exception:
#         pass
#     try:
#         m_data_obj.rate = target_m_data_obj.rate
#         m_data_obj.save()
#     except Exception:
#         pass
#     try:
#         m_data_obj.review_count = target_m_data_obj.review_count
#         m_data_obj.save()
#     except Exception:
#         pass

#     for o in target_r_objs:
#         r_obj, _ = models.Review.objects.update_or_create(
#             media=m_data_obj, content=o.content
#         )
#         try:
#             r_obj.title = o.title
#             r_obj.save()
#         except Exception:
#             pass
#         try:
#             r_obj.review_date = o.review_date
#             r_obj.save()
#         except Exception:
#             pass
#         try:
#             r_obj.log_num_byTabelog = o.log_num_byTabelog
#             r_obj.save()
#         except Exception:
#             pass
#         try:
#             r_obj.review_point = o.review_point
#             r_obj.save()
#         except Exception:
#             pass

#     target_store_obj.delete()

