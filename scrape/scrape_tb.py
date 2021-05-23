# from selenium import webdriver
# # from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException
# from time import sleep
# from bs4 import BeautifulSoup
# from googletrans import Translator

# import datetime
# from devtools import debug
# from pprint import pprint as pp

# from scrape import driver_settings
# from scrape import models
# from site_packages.my_module import *

# # area1 = "千葉県"
# # area2 = "船橋市"

# # あとで表示順のデータベースつくるか？
# media_type = "tb"

# # area_obj = models.Area.objects.get(area_name="千葉県 船橋市")
# # store_obj = models.Store.objects.filter(store_name__icontains="四季", area=area_obj)[2]
# # media_type_obj = models.Media_type.objects.get(media_type='tb')
# # media_obj = models.Media_data.objects.get(store=store_obj, media_type=media_type_obj)
# # media_obj = models.Media_data.objects.get(store=store_obj)
# # review_obj = models.Review.objects.filter(media=media_obj)

# # media_obj


# def scrape_tb(area1, area2, page_range):
#     print(area1+" "+area2)
#     media_type_obj = models.Media_type.objects.get(media_type=media_type)
#     area_obj, _ = models.Area.objects.get_or_create(area_name=area1+" "+area2)

#     def create_ignoreList():
#         area1_word = area1[:-1]
#         area2_word = area2 if area1 == "東京都" else area2[:-1]
#         ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
#         # ignore_listに英語も入れる
#         tr = Translator()
#         # del ignore_list[0] # 最初に入ってる空白を消す
#         add_ignore = []
#         for src in ignore_list[1:]:
#             try:
#                 en_word = tr.translate(src, src='ja', dest='en').text.lower()
#                 add_ignore.append(en_word)
#             except Exception as e:
#                 print(type(e), e)
#         ignore_list += add_ignore
#         ignore_list.append("store")
#         return ignore_list
#     ignore_list = create_ignoreList()

#     driver = webdriver.Chrome('chromedriver', options=driver_settings.options)
#     # driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
#     dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

#     driver.get('https://tabelog.com/')

#     area_input = driver.find_element_by_id('sa')
#     area_input.send_keys(f'{area2}' + Keys.ENTER)
#     sleep(2)

#     atode_list = []
#     created_list = []

#     try:
#         # for page_num in range(1, 5):  # いったん5ページ目まで
#         for page_num in page_range:  # いったん5ページ目まで
#             print(f'page_num: {page_num}')
#             try:
#                 driver.find_elements_by_class_name('c-pagination__num')[page_num].click()  # ページ
#             except Exception:
#                 pass

#             dw.wait_lacated_class_name('list-rst__rst-name-target')  # 最初のelementが現れるまで待つ
#             store_link_list = driver.find_elements_by_class_name('list-rst__rst-name-target')

#             for elem in store_link_list[:2]:
#                 atode_flg = False
#                 atode_dict = {}

#                 try:  # よくここでつまづく
#                     elem.click()
#                 except Exception:
#                     capture(driver)
#                     raise Exception()

#                 # webdriver.ActionChains(driver).key_down(Keys.COMMAND).click(elem).perform() # なぜかこれで新規タブで開くと、次の普通クリックでも新規タブが開く
#                 sleep(2)

#                 handle_array = driver.window_handles
#                 driver.switch_to.window(handle_array[-1])
#                 sleep(0.5)
#                 print('handle OK!')

#                 # store_name = driver.find_element_by_class_name('display-name').text
#                 store_name = dw.wait_lacated_class_name('display-name').text
#                 try:
#                     phone: str = driver.find_elements_by_class_name('rstinfo-table__tel-num')[-1].text
#                     type(int(phone.replace('-', ''))) == int  # 電話番号が非公開がたまにある
#                 except Exception:
#                     phone = ""
#                 # debug(store_name, phone)

#                 # 店名でstore_object取得  1番近いものを探すーーーー

#                 store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list, phone)

#                 atode_flg = _atode_flg
#                 atode_dict.update(_atode_dict)
#                 created_list += _created_list

#                 # media_data用ーーー
#                 store_url = driver.current_url
#                 rate = driver.find_element_by_class_name('rdheader-rating__score-val-dtl').text
#                 rate: float = 0 if rate == '-' else float(rate)
#                 review_count = driver.find_element_by_class_name('rdheader-rating__review-target').find_element_by_tag_name('em').text
#                 review_count: int = 0 if review_count == '-' else int(review_count)
#                 if atode_flg is False:
#                     media_obj, _ = models.Media_data.objects.update_or_create(
#                         store=store_obj, media_type=media_type_obj,
#                         defaults={
#                             "url": store_url,
#                             "rate": rate,
#                             "review_count": review_count,
#                         }
#                     )
#                 else:
#                     atode_dict["store_url"] = store_url
#                     atode_dict["rate"] = rate
#                     atode_dict["review_count"] = review_count

#                 # 口コミーーーーーーーーーー
#                 no_review_flg = False
#                 try:  # 口コミボタンが無い店もある
#                     driver.find_element_by_class_name('rstdtl-top-rvwlst__more-link').find_element_by_class_name('c-link-circle').click()
#                     sleep(1)
#                 except NoSuchElementException:
#                     no_review_flg = True
#                     print('口コミがありません。')
#                 else:
#                     dw.wait_lacated_link_text('訪問月順').click()
#                     sleep(1)
#                     print('口コミ発見！！')
#                     # 「もっと見る」を全て展開ーーーーーーーー
#                     mottomiru_list = driver.find_elements_by_class_name('js-show-review-items')[:6]  # 範囲制限
#                     for i in mottomiru_list:
#                         i.click()
#                         sleep(0.6)  # 早すぎるとバグる
#                     res = driver.page_source
#                     soup = BeautifulSoup(res, 'html.parser')
#                     items = soup.select('div.js-rvw-item-clickable-area')[:5]  # 範囲制限
#                     atode_review_list = []
#                     for item in items:  # 再訪は無視
#                         no_data_flg = False
#                         log = item.select('.rvw-item__rvwr-balloon-text')[0]
#                         log_num = int(log.text.replace(',', '').replace('ログ', ''))
#                         try:
#                             # title = item.select('.rvw-item__title')[0].text.replace('\n', '').replace('\u200b', '').replace('\u3000', '')
#                             title = item.select('.rvw-item__title')[0].text.strip()
#                         except IndexError:
#                             try:  # タイトルが無い投稿は本文の先頭24文字をとる。
#                                 # title = item.select('.rvw-item__rvw-comment')[0].text.replace('\u200b', '').replace('\u3000', '').strip()[:24] + "…"
#                                 title = item.select('.rvw-item__rvw-comment')[0].text.strip()[:24] + "…"
#                             except IndexError:  # 本文もない場合はpass
#                                 no_data_flg = True
#                                 print('no data!!')
#                         try:
#                             review_point = item.select_one('.c-rating-v2__val.c-rating-v2__val--strong.rvw-item__ratings--val').get_text(strip=True)
#                             review_point = float(review_point)
#                         except Exception:  # 評価値がついてない場合は0で入れるので、その後の表示等の処理を注意
#                             review_point = 0

#                         if no_data_flg is False:
#                             content = item.select('.rvw-item__rvw-comment')[0]
#                             # <br>タグを\nに置き換える
#                             [s.replace_with('\n') for s in content.select('br')]
#                             # content = content.text.replace('\u200b', '').replace('\u3000', '').strip()
#                             content = content.text.strip()
#                             print(content)

#                             try:  # 日時が「行った 〜〜」とあるときがある。
#                                 for date_elem in item.select('div.rvw-item__single-date'):
#                                     review_date = date_elem.get_text(strip=True)[:-2]
#                                     review_date = datetime.datetime.strptime(review_date, '%Y/%m')
#                                     break
#                             except ValueError:
#                                 review_date = None

#                             if atode_flg is False:
#                                 models.Review.objects.update_or_create(
#                                     media=media_obj, title=title, defaults={
#                                         "content": content,
#                                         "review_date": review_date,
#                                         "log_num_byTabelog": log_num,
#                                         "review_point": review_point,
#                                     }
#                                 )
#                                 debug(log_num, review_point, review_date, title)
#                                 print('レビュー登録!!')
#                             else:
#                                 # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
#                                 # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
#                                 atode_review_dict = {}
#                                 atode_review_dict["title"] = title
#                                 atode_review_dict["content"] = content
#                                 atode_review_dict["date"] = review_date
#                                 atode_review_dict["log_num"] = log_num
#                                 atode_review_dict["review_point"] = review_point
#                                 atode_review_list.append(atode_review_dict)

#                     # atode処理ーーーーーーーーー
#                     if atode_dict:
#                         atode_dict["review"] = atode_review_list
#                     # ーーーーーーーーーーーー
#                 if atode_dict:
#                     atode_list.append(atode_dict)

#                 driver.execute_script("window.close();")
#                 driver.switch_to.window(handle_array[0])
#                 sleep(1)

#         print('作成は、')
#         pp(created_list)
#     except Exception as e:
#         print(type(e))
#         print(e)
#         print(f'えらー {page_num} キャプチャ！')
#         capture(driver)
#         driver.quit()
#         raise Exception()
#     # ーーーーーatode処理ーーーーーーーーーー
#     # [{"store_name_db":a,"store_name_site":a,"phone":a,"store_url":a,"rate":a,
#     # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
#     #  {"name":a, ..........}]
#     if atode_list:
#         _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

#         created_list += _created_list

#         print('作成は、')
#         pp(created_list)
#         print('不採用は、')
#         pp(not_adopted_list)

#     driver.quit()
