from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup
from googletrans import Translator

import datetime
from devtools import debug
from pprint import pprint as pp

from scrape import driver_settings
from scrape import models
from site_packages.my_module import *

# area1 = "千葉県"
# area2 = "船橋市"

media_type = "gn"

# area_obj = models.Area.objects.get(area_name="千葉県 船橋市")
# store_obj = models.Store.objects.filter(store_name__icontains="四季", area=area_obj)[2]
# media_type_obj = models.Media_type.objects.get(media_type='tb')
# media_obj = models.Media_data.objects.get(store=store_obj, media_type=media_type_obj)
# media_obj = models.Media_data.objects.get(store=store_obj)
# review_obj = models.Review.objects.filter(media=media_obj)

# media_obj


def scrape_gn(area1, area2, page_range):
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

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    driver.get('https://www.gnavi.co.jp/')

    area_input = driver.find_element_by_id('js-suggest-area')
    area_input.send_keys(area1)
    driver.find_element_by_class_name('p-search__button').click()
    sleep(2)

    driver.find_element_by_class_name('search-group__block-trigger').click()
    driver.find_element_by_xpath(f"//a[contains(@data-value,'{area2[:-1]}')]").click()
    driver.find_element_by_xpath("//input[@value='検索する']").click()
    sleep(1)
    driver.find_element_by_class_name('search-group__block-trigger').click()
    driver.find_element_by_link_text('市区町村').click()
    driver.find_element_by_link_text(area2).click()
    driver.find_element_by_xpath("//input[@value='検索する']").click()

    atode_list = []
    created_list = []

    try:
        # for page_num in range(1, 5):  # いったん5ページ目まで
        for page_num in page_range:  # いったん5ページ目まで
            try:
                driver.find_element_by_class_name('pagination__inner').find_element_by_link_text(f'{page_num}').click()
            except Exception:
                pass

            store_link_list = driver.find_elements_by_class_name('result-cassette__box-inner')
            for elem in store_link_list:
                sleep(1)
                atode_flg = False
                atode_dict = {}

                elem.click()

                sleep(2)

                handle_array = driver.window_handles
                driver.switch_to.window(handle_array[-1])
                sleep(0.5)
                print('handle OK!')

                store_name = driver.find_element_by_class_name('shop-info__name').text.strip()
                store_name = " ".join(store_name.split('\n'))  # ぐるなび用 店名が2行にわかれてる

                # 店名でstore_object取得  1番近いものを探すーーーー

                store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list)

                atode_flg = _atode_flg
                atode_dict.update(_atode_dict)
                created_list += _created_list

                # media_data用ーーー
                store_url = driver.current_url

                if atode_flg is False:
                    media_obj, _ = models.Media_data.objects.update_or_create(
                        store=store_obj, media_type=media_type_obj,
                        defaults={
                            "url": store_url,
                        }
                    )
                else:
                    atode_dict["store_url"] = store_url

                # 口コミーーーーーーーーーー
                no_review_flg = False
                driver.find_element_by_link_text('口コミ').click()
                sleep(1)
                res = driver.page_source
                soup = BeautifulSoup(res, 'html.parser')

                try:
                    rate = driver.find_element_by_class_name('trip-advisor-rating-img').get_attribute('alt')
                    rate = float(rate)
                except Exception:
                    rate = 0
                    print('no rate')

                try:  # 口コミボタンが無い店もある
                    review_count = len(soup.select('li.trip-advisor-review__list'))
                    if review_count == 0:
                        raise Exception
                except Exception:
                    no_review_flg = True
                    print('口コミがありません。')
                else:
                    print('口コミ発見！！')

                    # 「もっと見る」を全て展開ーーーーーーーー
                    tsuzukiwoyomu_list = driver.find_elements_by_class_name('plus')[:4]  # 範囲制限
                    for i in tsuzukiwoyomu_list:
                        i.click()
                        # sleep(0.6)  # 早すぎるとバグる
                    items = soup.select('li.trip-advisor-review__list')[:4]  # 範囲制限
                    atode_review_list = []
                    for item in items:
                        no_data_flg = False
                        try:
                            title = item.select_one('.trip-advisor-review-title').text.strip()
                        except IndexError:
                            try:  # タイトルが無い投稿は本文の先頭24文字をとる。
                                title = item.select_one('.trip-advisor-review-text').text.strip()[:24] + "…"
                            except IndexError:  # 本文もない場合はpass
                                no_data_flg = True
                                print('no data!!')
                        try:
                            review_point = item.select_one('.trip-advisor-review-rating').select_one('img').get('alt')
                            review_point = int(review_point)
                            print(f'get point {review_point}点')
                        except Exception:  # 評価値がついてない場合は0で入れるので、その後の表示等の処理を注意
                            review_point = 0
                            print("can't get point...")

                        if no_data_flg is False:
                            content = item.select_one('.trip-advisor-review-text')
                            # content = items[1].select_one('.trip-advisor-review-text')
                            # content = "".join([s.text for s in content]).strip()
                            # <br>タグを\nに置き換える
                            [s.replace_with('\n') for s in content.select('br')]
                            content = content.text
                            print(content)

                            try:
                                review_date = item.select_one('.trip-advisor-review-day--visit').text
                                review_date = review_date[review_date.find('：')+1:review_date.find('）')]
                                review_date = datetime.datetime.strptime(review_date, '%Y年%m月')
                                print(review_date)
                            except ValueError:
                                review_date = None

                            if atode_flg is False:
                                models.Review.objects.update_or_create(
                                    media=media_obj, title=title, defaults={
                                        "content": content,
                                        "review_date": review_date,
                                        "review_point": review_point,
                                    }
                                )
                                debug(review_point, review_date, title)
                                print('レビュー登録!!')
                            else:
                                # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                                # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                                atode_review_dict = {}
                                atode_review_dict["title"] = title
                                atode_review_dict["content"] = content
                                atode_review_dict["date"] = review_date
                                atode_review_dict["review_point"] = review_point
                                atode_review_list.append(atode_review_dict)

                    # atode処理ーーーーーーーーー
                    if atode_dict:
                        atode_dict["review"] = atode_review_list
                    # ーーーーーーーーーーーー

                if atode_flg is False:
                    media_obj, _ = models.Media_data.objects.update_or_create(
                        store=store_obj, media_type=media_type_obj,
                        defaults={
                            "rate": rate,
                            "review_count": review_count,
                        }
                    )
                else:
                    atode_dict["rate"] = rate
                    atode_dict["review_count"] = review_count

                if atode_dict:
                    atode_list.append(atode_dict)

                driver.execute_script("window.close();")
                driver.switch_to.window(handle_array[0])
                sleep(1)

        print('作成は、')
        pp(created_list)
    except Exception as e:
        print(type(e))
        print(e)
        print(f'えらー {page_num} キャプチャ！')
        capture(driver)
        driver.quit()
        raise Exception()
    # ーーーーーatode処理ーーーーーーーーーー
    # [{"store_name_db":a,"store_name_site":a,"phone":a,"store_url":a,"rate":a,
    # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
    #  {"name":a, ..........}]
    if atode_list:
        _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        created_list += _created_list

        print('作成は、')
        pp(created_list)
        print('不採用は、')
        pp(not_adopted_list)

    driver.quit()
