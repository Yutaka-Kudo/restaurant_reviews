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
from dateutil.relativedelta import relativedelta

from scrape import driver_settings
from scrape import models
from site_packages.my_module import *

# area1 = "千葉県"
# area2 = "船橋市"
media_type = "google"


def scrape_google(area1, area2, page_range):
    print(area1+" "+area2)
    media_type_obj = models.Media_type.objects.get(media_type=media_type)
    area_obj, _ = models.Area.objects.get_or_create(area_name=area1+" "+area2)

    compare_store_name = Compare_storeName()
    store_objs = models.Store.objects.filter(area=area_obj)

    def create_ignoreList():
        area1_word = area1[:-1]
        area2_word = area2 if area1 == "東京都" else area2[:-1]
        ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
        # ignore_listに英語も入れる
        tr = Translator()
        # del ignore_list[0] # 最初に入ってる空白を消す
        add_ignore = []
        for src in ignore_list:
            try:
                en_word = tr.translate(src, src='ja', dest='en').text.lower()
                add_ignore.append(en_word)
            except Exception as e:
                print(e)
        ignore_list += add_ignore
        ignore_list.append("store")
        return ignore_list
    ignore_list = create_ignoreList()

    # driver = webdriver.Chrome('chromedriver', options=driver_settings.options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    driver.get('https://google.com/')

    area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
    area_input.send_keys(f'{area1+area2} 居酒屋' + Keys.ENTER)
    sleep(2)

    driver.find_element_by_link_text('すべて表示').click()

    created_list = []
    atode_list = []

    try:
        debug_list = []
        first_page_flg = True

        for page_num in page_range:  # ページーーーーーーーーーーーーー
            debug(page_num)
            try:
                driver.find_element_by_xpath(f"//a[@aria-label='Page {page_num}']").click()
                # driver.find_element_by_link_text('次へ').click()
                # driver.refresh()
            except Exception:
                pass
            sleep(3)

            # 1ページ目の広告枠＋3個のあとにおすすめページに誘われるのでそこをスルー
            # store_list_wrap = driver.find_element_by_css_selector('div.rl_tile-group > div:nth-of-type(4)')
            class_details = driver.find_elements_by_xpath("//span[contains(@class,'__details')]")
            ad_count = 0
            for c in class_details:
                if c.text.count('広告'):
                    ad_count += 1
            print("ad_count: " + str(ad_count))

            for store_num in range(1, 21):  # 店ーーーーーーーーーーーーーーーー
                # for store_num in range(1, 2):
                atode_dict = {}
                atode_flg = False
                ng_flg = False
                sleep(1)
                if first_page_flg is True and store_num == ad_count + 4:
                    first_page_flg = False
                    print('skip!!!!')
                else:
                    debug(store_num)
                    driver.find_element_by_css_selector(f'div.rl_full-list > div > div > div > div:nth-child(4) > div:nth-child({store_num})').click()
                    sleep(1)
                    store_name = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div > div > div > h2').text
                    # akp_tsuid137 > div > div:nth-child(1) > div > div > div > div.kp-blk.knowledge-panel.Wnoohf.OJXvsb > div > div.ifM9O > div > div.kp-header > div > div:nth-child(2) > div:nth-child(1) > div > div > span.hqzQac > span > a > span
                    debug(store_name)

                    if store_name == "居酒屋":  # 多分Googleだけ、変な名前、登録データなしでつまる。
                        ng_flg = True
                    if ng_flg == False:
                        try:
                            phone = driver.find_element_by_xpath('/html/body/div[6]/div/div[8]/div[2]/div/div[2]/async-local-kp/div/div/div[1]/div/div/div/div[1]/div/div[1]/div').find_element_by_xpath("//span[@role='link']").text
                            type(int(phone.replace('-', ''))) == int  # 電話番号が非公開がたまにある
                            debug(phone)
                        except Exception:
                            print('no phone!')
                            phone = None

                        # 店名でstore_object取得  1番近いものを探すーーーー
                        store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list, phone)
                        atode_flg = _atode_flg
                        atode_dict.update(_atode_dict)
                        created_list += _created_list

                        # media_data用ーーー
                        store_url = driver.current_url
                        rate = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span').text
                        try:
                            rate: float = 0 if rate == '-' else float(rate)
                        except Exception:
                            rate = 0
                        if atode_flg is False:
                            media_obj, _ = models.Media_data.objects.update_or_create(
                                store=store_obj, media_type=media_type_obj,
                                defaults={
                                    "url": store_url,
                                    "rate": rate,
                                }
                            )
                        else:
                            atode_dict["store_url"] = store_url
                            atode_dict["rate"] = rate

                        atode_review_list = []
                        try:
                            driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span:nth-child(3) > span > a').click()  # 口コミボタンクリック
                        except Exception:
                            ng_flg = True

                    def collect_review(second_time=False):
                        sleep(2)
                        for review_num in range(1, 6):
                            no_content_flg = False
                            try:  # 「もっと見る」があるかないか
                                driver.find_element_by_css_selector(f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num})').find_element_by_class_name('review-more-link').click()
                                sleep(0.5)
                                content = driver.find_element_by_css_selector(
                                    f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(2) > span > span:nth-of-type(2)').text
                            except Exception:
                                try:
                                    # sleep(0.3)
                                    content = driver.find_element_by_css_selector(f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(2) > span').text
                                except Exception:
                                    content = ""
                                finally:
                                    if not content:  # コンテンツがなければor取得失敗したら
                                        no_content_flg = True

                            if not no_content_flg:

                                # 日付け処理ーーーーー
                                review_date = driver.find_element_by_css_selector(f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div > span:nth-of-type(1)').text
                                splited = review_date.split(' ')
                                today = datetime.datetime.today()
                                if splited[1] == "時間前":
                                    review_date = (today - relativedelta(hours=int(splited[0]))).date() + relativedelta(day=1)
                                elif splited[1] == "日前":
                                    review_date = (today - relativedelta(days=int(splited[0]))).date() + relativedelta(day=1)
                                elif splited[1] == "週間前":
                                    review_date = (today - relativedelta(weeks=int(splited[0]))).date() + relativedelta(day=1)
                                elif splited[1] == "か月前":
                                    review_date = (today - relativedelta(months=int(splited[0]))).date() + relativedelta(day=1)
                                elif splited[1] == "年前":
                                    review_date = (today - relativedelta(years=int(splited[0]))).date() + relativedelta(day=1)
                                else:
                                    debug_list.append(store_name)
                                    debug_list.append(review_date)
                                    debug_list.append(content)
                                    review_date = today.date() + relativedelta(day=1)

                                # ポイント処理ーーーー
                                review_point = driver.find_element_by_css_selector(
                                    f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div > g-review-stars > span').get_attribute('aria-label')  # '5 点中 4.0 点の評価、'
                                splited = review_point.split(' ')
                                review_point = float(splited[2])

                                if atode_flg is False:
                                    if second_time is True and review_num == 1:  # 初期ループ時にデータ消して刷新
                                        models.Review.objects.filter(media=media_obj).delete()
                                        print('ReviewObj delete for renewal')

                                    debug(review_date, review_point, content)
                                    try:
                                        models.Review.objects.update_or_create(
                                            media=media_obj, content=content, defaults={
                                                "review_date": review_date,
                                                "review_point": review_point,
                                            }
                                        )
                                        print('insert review!!')
                                    except Exception:
                                        pass
                                else:
                                    # {"name in name_list:":a,"name in name_list:":a,"phone":a,"url":a,"rate":a,
                                    # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                                    atode_review_dict = {}
                                    atode_review_dict["content"] = content
                                    atode_review_dict["date"] = review_date
                                    atode_review_dict["review_point"] = review_point
                                    atode_review_list.append(atode_review_dict)

                    if not ng_flg:
                        collect_review()
                        try:
                            driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(2) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
                            collect_review(second_time=True)  # もう一回
                            sleep(1)
                        except Exception:
                            try:
                                driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(3) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
                                collect_review(second_time=True)  # もう一回
                                sleep(1)
                            except Exception:
                                print('新規順クリックerror!!!!!!!!!')

                        sleep(1)

                        # driver.find_element_by_xpath(f'/html/body/span[{store_num}]/g-lightbox/div[2]/div[2]').click() # 閉じるボタン
                        actions = webdriver.ActionChains(driver)
                        actions.send_keys(Keys.ESCAPE).perform()  # 閉じる

                        # atode処理ーーーーーーーーー
                        if atode_dict:
                            atode_dict["review"] = atode_review_list
                        # ーーーーーーーーーーーー
                    if atode_dict:
                        atode_list.append(atode_dict)

            driver.find_element_by_xpath("//button[@aria-label='Google 検索']").click()  # リフレッシュ
            sleep(2)

    except Exception as e:
        print('作成は、')
        pp(created_list)
        print(e)
        print(f'えらー {page_num} {store_num} キャプチャ！')
        capture(driver)
        driver.quit()
    # ーーーーーatode処理ーーーーーーーーーー
    # [{"store_name_db":a,"store_name_site":a,"phone":a,"store_url":a,"rate":a,
    # "review":[{"title":a,"content":a,"date":a,"log_num":a},{....},{.....}]},
    #  {"name in name_list:":a, ..........}]

    not_adopted_list = []
    if atode_list:
        _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        created_list += _created_list

    print('作成は、')
    pp(created_list)
    print('不採用は、')
    pp(not_adopted_list)
    print('デバッグリスト')
    pp(debug_list)

    driver.quit()


def scrape_google_get_storenames(area1, area2, page_range):
    print(area1+" "+area2)
    media_type_obj = models.Media_type.objects.get(media_type=media_type)
    area_obj, _ = models.Area.objects.get_or_create(area_name=area1+" "+area2)
    area1_word = area1[:-1]
    area2_word = area2 if area1 == "東京都" else area2[:-1]
    ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]

    atode_list = []
    created_list = []

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)

    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    driver.get('https://google.com/')

    area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
    area_input.send_keys(f'{area1+area2} 居酒屋' + Keys.ENTER)
    sleep(2)

    driver.find_element_by_link_text('すべて表示').click()

    try:
        debug_list = []
        is_first_page = True
        for page_num in page_range:  # ページーーーーーーーーーーーーーーー
            debug(page_num)
            try:
                driver.find_element_by_xpath(f"//a[@aria-label='Page {page_num}']").click()
                # driver.find_element_by_link_text('次へ').click()
                # driver.refresh()
            except Exception:
                pass
            sleep(2)

            # 1ページ目の広告枠＋3個のあとにおすすめページに誘われるのでそこをスルー
            # store_list_wrap = driver.find_element_by_css_selector('div.rl_tile-group > div:nth-of-type(4)')
            try:
                class_details = driver.find_elements_by_xpath("//span[contains(@class,'__details')]")
                ad_count = 0
                for c in class_details:
                    if c.text.count('広告'):
                        ad_count += 1
                print("ad_count: " + str(ad_count))
            except Exception:
                print("ad_count: no get")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                name_class = soup.select_one(f".rlfl__tls.rl_tls > div:nth-of-type({ad_count+1}) > div > div:nth-of-type(3) > div > a > div > div:nth-of-type(2)").get('class')[0]
            except Exception:
                name_class = soup.select_one(f".rlfl__tls.rl_tls > div:nth-of-type({ad_count+1}) > div > div:nth-of-type(2) > div > a > div > div:nth-of-type(2)").get('class')[0]
            try:
                # rate_class = soup.select("span[class*='__details']")[ad_count+1].select_one(f'div > span:nth-of-type({1})').get('class')[0]
                rate_class = soup.select(".rlfl__tls.rl_tls > div")[ad_count:]
            except Exception:
                # rate_class = soup.select("span[class*='__details']")[ad_count+2].select_one(f'div > span:nth-of-type({1})').get('class')[0]
                pass

            name_list = []
            rate_list = []
            review_count_list = []

            name_class_list = soup.select(f".{name_class}")
            del name_class_list[:ad_count]
            for c in name_class_list:
                name_list.append(c.text)

            # rate_class_list = soup.select(f".{rate_class}")
            # ad_count -= 20 - len(rate_class_list)
            if is_first_page is True:
                del rate_class[3]  # 4つ目が広告
                is_first_page = False

            try:
                for c in rate_class[:-1]:
                    rate = c.select_one("span[class*='__details']").select_one(f'div > span:nth-of-type({1})').text
                    try:
                        rate = float(rate)
                    except Exception:
                        rate = 0
                    rate_list.append(rate)

                    review_count = c.select_one("span[class*='__details']").select_one(f'div > span:nth-of-type({1}) ~ span').text
                    try:
                        review_count = int(review_count.strip('()'))
                    except ValueError as e:
                        print(e)
                        print('review_count = 0 にします')
                        review_count = 0

                    review_count_list.append(review_count)
            except Exception:
                pass

            debug(len(name_list), len(review_count_list), len(rate_list))
            if not len(name_list) == len(rate_list) == len(review_count_list):
                print('length NG...')
            else:
                print("length OK!!")

                # 店名でstore_object取得  1番近いものを探すーーーー
                for i, store_name in enumerate(name_list):
                    atode_flg = False
                    atode_dict = {}

                    store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list)
                    atode_flg = _atode_flg
                    atode_dict.update(_atode_dict)
                    created_list += _created_list

                    if not atode_flg:
                        models.Media_data.objects.update_or_create(
                            store=store_obj, media_type=media_type_obj, defaults={
                                "rate": rate_list[i],
                                "review_count": review_count_list[i],
                            }
                        )
                        print('update media_data!!')
                    else:
                        atode_dict["rate"] = rate_list[i]
                        atode_dict["review_count"] = review_count_list[i]

                        atode_list.append(atode_dict)

        print('作成は、')
        pp(created_list)
    except Exception as e:
        capture(driver)
        print(f'えらー {e} {page_num}ページ キャプチャ！')
        driver.quit()

    # atode処理ーーーーーー
    not_adopted_list = []
    if atode_list:
        _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

    print('作成は、')
    pp(created_list)
    print('不採用は、')
    pp(not_adopted_list)
    print('デバッグリスト')
    pp(debug_list)

    driver.quit()
