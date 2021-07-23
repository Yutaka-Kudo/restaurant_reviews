# from selenium import webdriver
# from selenium.webdriver.common import keys
# from webdriver_manager.chrome import ChromeDriverManager
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
# media_type = "hp"

# area_obj = models.Area.objects.get(area_name="千葉県 船橋市")
# store_obj = models.Store.objects.filter(store_name__icontains="963", area=area_obj)[1]
# media_type_obj = models.Media_type.objects.get(media_type='tb')
# media_obj = models.Media_data.objects.get(store=store_obj, media_type=media_type_obj)
# review_obj = models.Review.objects.filter(media=media_obj)

# def hover(elem):
#     actions = webdriver.ActionChains(driver)
#     actions.move_to_element(elem).perform()  # ホバー

from selenium import webdriver
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup

import datetime
import pytz
from devtools import debug
from pprint import pprint as pp
from dateutil.relativedelta import relativedelta

import json
import re

from scrape import driver_settings

try:
    from my_module import capture, Wait_located
    from scrape_kit import generate_json, endpage_memo, address_ng_memo
except ImportError:
    from site_packages.my_module import capture, Wait_located
    from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo


from site_packages.my_module import collectStoreOtherThanThat



def scrape_hp(area1, area2, page_range):
    print(area1+" "+area2)
    media_type_obj = models.Media_type.objects.get(media_type=media_type)
    area_obj, _ = models.Area.objects.get_or_create(area_name=area1+" "+area2)

    def create_ignoreList():
        area1_word = area1[:-1]
        area2_word = area2 if area1 == "東京都" else area2[:-1]
        ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
        # ignore_listに英語も入れる
        tr = Translator()
        # del ignore_list[0] # 最初に入ってる空白を消す
        add_ignore = []
        for src in ignore_list[1:]:
            try:
                en_word = tr.translate(src, src='ja', dest='en').text.lower()
                add_ignore.append(en_word)
            except Exception as e:
                print(type(e), e)
        ignore_list += add_ignore
        ignore_list.append("store")
        return ignore_list
    ignore_list = create_ignoreList()

    # driver = webdriver.Chrome('chromedriver', options=driver_settings.options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    driver.get('https://www.hotpepper.jp/')

    dw.wait_lacated_class_name('areaSelectList').find_element_by_link_text(area1[:-1]).click()
    sleep(1)

    driver.find_element_by_class_name('jscFreeWordSearch.jscFreewordSearchTxt.example').send_keys(area2[:-1] + Keys.ENTER)
    sleep(1)

    atode_list = []
    created_list = []

    try:
        for page_num in page_range:  # いったん5ページ目まで
            try:
                driver.find_element_by_class_name('pageLinkLinearBasic').find_element_by_link_text(f'{page_num}').click()  # ページ
            except Exception:
                pass

            sleep(1)

            store_link_list = driver.find_elements_by_css_selector('.shopDetailStoreName > a')

            for i in range(len(store_link_list)):
            # for i in range(len(store_link_list)):
                store_link_list = driver.find_elements_by_css_selector('.shopDetailStoreName > a')  # 再度認識が必要
                atode_flg = False
                atode_dict = {}

                # store_link_list[1].click()
                store_link_list[i].click()

                sleep(0.5)
                print('handle OK!')

                store_name = dw.wait_lacated_xpath("//h1[@class='shopName']").text

                # 店名でstore_object取得  1番近いものを探すーーーー

                store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list)

                atode_flg = _atode_flg
                atode_dict.update(_atode_dict)
                created_list += _created_list

                # media_data用ーーー
                store_url = driver.current_url
                try:
                    rate = driver.find_element_by_class_name('ratingScoreValue').text
                    rate: float = 0 if rate == '-' else float(rate)
                except NoSuchElementException:
                    rate = 0
                try:
                    review_count = driver.find_elements_by_css_selector('p.recommendReportNum > span')[1].text
                    review_count: int = 0 if review_count == '-' else int(review_count)
                except IndexError:
                    review_count = 0

                if atode_flg is False:
                    media_obj, _ = models.Media_data.objects.update_or_create(
                        store=store_obj, media_type=media_type_obj,
                        defaults={
                            "url": store_url,
                            "rate": rate,
                            "review_count": review_count,
                        }
                    )
                else:
                    atode_dict["store_url"] = store_url
                    atode_dict["rate"] = rate
                    atode_dict["review_count"] = review_count

                # 口コミーーーーーーーーーー
                try:  # 口コミボタンが無い店もある
                    driver.find_element_by_partial_link_text('口コミ').click()
                    sleep(1)
                except NoSuchElementException:
                    print('口コミがありません。')
                else:
                    print('口コミ発見！！')
                    sleep(1)
                    atode_review_list = []
                    subeteyomu: list = driver.find_elements_by_class_name('arrowLink')
                    subeteyomu = subeteyomu[:4]  #範囲限定
                    for i in range(len(subeteyomu)):
                        sleep(1)
                        subeteyomu: list = driver.find_elements_by_class_name('arrowLink')  # 再度認識が必要
                        subeteyomu[i].click()
                        sleep(0.5)
                        individual = driver.find_element_by_class_name('individualInfo').text

                        review_date = datetime.datetime.strptime(individual.split('：')[-1], '%Y/%m/%d').date()

                        content = driver.find_element_by_class_name('reportText').text

                        print(repr(content[:100]))

                        if atode_flg is False:
                            models.Review.objects.update_or_create(
                                media=media_obj, content=content, defaults={
                                    "review_date": review_date,
                                }
                            )
                            debug(review_date)
                            print('レビュー登録!!')
                        else:
                            # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                            # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                            atode_review_dict = {}
                            atode_review_dict["content"] = content
                            atode_review_dict["date"] = review_date
                            atode_review_list.append(atode_review_dict)

                        driver.back()

                    # atode処理ーーーーーーーーー
                    if atode_dict:
                        atode_dict["review"] = atode_review_list
                    # ーーーーーーーーーーーー

                    driver.back()
                    print('back!!!')

                    sleep(1)

                if atode_dict:
                    atode_list.append(atode_dict)

                driver.back()
                print('back!!!')

                sleep(2)

        print('作成は、')
        pp(created_list)
    except Exception as e:
        print(type(e))
        print(e)
        err = e
        print(f'えらー {page_num} キャプチャ！')
        capture(driver)
        driver.quit()
        # raise Exception()
    # ーーーーーatode処理ーーーーーーーーーー
    # [{"store_name_db":a,"store_name_site":a,"phone":a,"store_url":a,"rate":a,
    # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
    #  {"name":a, ..........}]
    finally:
        if atode_list:
            _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

            created_list += _created_list

            print('作成は、')
            pp(created_list)
            print('不採用は、')
            pp(not_adopted_list)

        # driver.quit()

        try:  # エラーがあれば最後に掲示
            print(type(err))
            print(err)
        except Exception:
            pass
    driver.quit()

