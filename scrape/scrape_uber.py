from scrape import driver_settings
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup

from devtools import debug
from pprint import pprint as pp
from googletrans import Translator

from scrape import models
from site_packages.my_module import *

# area1 = "千葉県"
# area2 = "船橋市"

media_type = "uber"


def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def isnoblank(word: str):
    word = word.replace(' ', '')
    return word.isalnum()


def scrape_uber(area1, area2):
    print(area1+" "+area2)
    media_type_obj = models.Media_type.objects.get(media_type=media_type)
    area_obj, _ = models.Area.objects.get_or_create(area_name=area1+" "+area2)

    # driver = webdriver.Chrome('chromedriver', options=driver_settings.options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)

    driver.get('https://www.ubereats.com/jp/')

    input_area = driver.find_element_by_id('location-typeahead-home-input')
    input_area.send_keys(f'{area1}{area2}')
    sleep(2)
    input_area.send_keys(Keys.ENTER)

    # 「最も人気の料理」ーーーーーーーーーー
    sleep(2)
    try:
        driver.find_element_by_xpath("//span[contains(text(), '並べ替え')]").click()
        driver.find_element_by_xpath("//span[contains(text(), '  最も人気の料理')]").click()
        # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()  # TOP画面用
    except Exception:
        driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()
        # dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()
        # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()  # ラジオボタン押下後の画面用 保険で

    # さらに表示ーーーーーーーーーー
    next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
    next_btn = driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
    while next_btn:
        try:
            next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
            # next_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div[2]/div/button')))
            # sleep(1)
            next_btn.click()
        except Exception:
            next_btn = None
        print("next_btn")

    # res = driver.page_source
    # soup法
    # soup = BeautifulSoup(res, 'html.parser')
    # 全体を取れるが、点数ついてない店があったら、ずれる。「新着」ならOKですーーーーーー
    # store_names = [n.text for n in soup.select('.h3.cq.ce.cp.an.al.m0.bu')]
    # store_names = [n.text for n in soup.select('.be.bf.bg.g2.an.al.kc.bh')] #たぶん、一定時間でクラス名変わる。スクレイピング対策か
    # rate = [n.text for n in soup.select('div.gt.cd.ce.ec.eb.iu')]
    # debug(list(zip(store_names,rate)))
    # len(store_names)
    # len(rate)

    # driver法

    def get_data():
        count = 1
        elem = dw.wait_lacated_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{1}]/div/a/div/div[1]/p')

        while elem:
            try:
                elem = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{count}]/div/a/div/div[1]/p')
            except NoSuchElementException:
                elem = None
                count -= 1
            else:
                count += 1

        debug_list = []
        datalist = []

        for i in range(1, count+1):
            dict = {}
            dict["store_name"] = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div[1]/p').text

            try:  # html構成がちょくちょくかわる
                dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[3]/div/span[1]').text)
            except (ValueError, NoSuchElementException):
                try:
                    dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[2]/div/span[1]').text)
                except (ValueError, NoSuchElementException):
                    dict["rate"] = 0

            try:  # html構成がちょくちょくかわる
                dict["review_count"] = int(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[3]/div/span[3]').text.replace("(", "").replace(")", "").replace("+", ""))
            except (ValueError, NoSuchElementException):
                try:
                    dict["review_count"] = int(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[2]/div/span[3]').text.replace("(", "").replace(")", "").replace("+", ""))
                except (ValueError, NoSuchElementException):
                    dict["review_count"] = 0

            dict["url"] = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/figure/a').get_attribute('href')
            for k, v in dict.items():
                if not v:
                    # debug(dict)
                    print('取得結果が空です。')
                    debug_list.append(dict)
                    break

            datalist.append(dict)
            print(dict["store_name"])
        return datalist, debug_list

    datalist, debug_list = get_data()

    driver.quit()

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

    created_list = []
    atode_list = []

    # 一旦削除
    models.Media_data.objects.filter(store__area=area_obj, media_type=media_type_obj).delete()

    for store in datalist:
        atode_flg = False
        atode_dict = {}

        store_name = store["store_name"]
        rate = store["rate"]
        store_url = store["url"]
        review_count = store["review_count"]

        store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list)

        atode_flg = _atode_flg
        atode_dict.update(_atode_dict)
        created_list += _created_list

        # media_data用ーーー
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

        # # レビューカウント用
        # media_obj = models.Media_data.objects.get(store=store_obj, media_type=media_type_obj)
        # review_count = len(models.Review.objects.filter(media=media_obj))
        # if atode_flg is False:
        #     models.Media_data.objects.update_or_create(
        #         store=store_obj, media_type=media_type_obj, defaults={
        #             "review_count": review_count,
        #         }
        #     )

        # atode処理ーーーーーーーーー
        if atode_dict:
            atode_list.append(atode_dict)
        # ーーーーーーーーーーーー

    # except Exception as e:
    #     print(e)
    #     capture(driver)
    #     print(f'えらー {page_num} キャプチャ！')
    #     driver.quit()

    if atode_list:
        _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        created_list += _created_list
        print('不採用は、')
        pp(not_adopted_list)

    if input('clean_store_objする？y/n: ') == "y":
        clean_store_obj(area_obj)

    print('作成は、')
    pp(created_list)
    print('デバッグリスト、')
    pp(debug_list)


