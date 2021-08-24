# from scrape import driver_settings
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from bs4 import BeautifulSoup
import datetime
import random
import re

from devtools import debug
from pprint import pprint as pp
from googletrans import Translator

from scrape import models
from site_packages.my_module import capture, Wait_located
from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo
from site_packages import sub

media_type = "uber"

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')

user_agent = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
]
# options.add_argument('--user-data-dir=' + profile_path)
now_ua = user_agent[random.randrange(0, len(user_agent), 1)]
options.add_argument('--user-agent=' + now_ua)
options.add_argument('--disable-desktop-notifications')
options.add_argument("--disable-extensions")
options.add_argument('--lang=ja')
options.add_argument('--blink-settings=imagesEnabled=false')  # 画像なし
options.add_argument('--no-sandbox')
# options.binary_location = '/usr/bin/google-chrome'
options.add_argument('--proxy-bypass-list=*')      # すべてのホスト名
options.add_argument('--proxy-server="direct://"')  # Proxy経由ではなく直接接続する
# if chrome_binary_path:
#     options.binary_location = chrome_binary_path
# options.add_argument('--single-process')
# options.add_argument('--disable-application-cache')
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--start-maximized')

options.add_argument('--window-size=1200,700')


def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def isnoblank(word: str):
    word = word.replace(' ', '').replace('　', '')
    return word.isalnum()


def scrape_uber():

    # area1 = "千葉県"
    # area2s = [
    #     # "船橋市",
    #     # "市川市",
    #     # "千葉市",
    #     # "柏市",

    #     # "松戸市",
    #     # "銚子市",
    #     # "館山市",
    #     # "習志野市",
    #     "木更津市",
    #     # "",
    # ]
    area1 = "東京都"
    area2s = [
        # "青山一丁目駅",
        # "赤羽駅",
        "秋葉原駅",
        # "浅草駅",
        # "麻布十番駅",
        # "池袋駅",
        # "板橋駅",
        # "上野駅",
        # "恵比寿駅",
        # "大久保駅",
        # "お台場海浜公園駅",
        # "北千住駅",
        # "吉祥寺駅",
        # "銀座駅",
        # "国分寺駅",
        # "三軒茶屋駅",
        # "渋谷駅",
        # "新宿駅",
        # "新橋駅",
        # "自由が丘駅",
        # "水道橋駅",
        # "高田馬場駅",
        # "中野駅",
        # "中目黒駅",
        # "日本橋駅",
        # "練馬駅",
        # "原宿駅",
        # "二子玉川駅",
        # "町田駅",
        # "有楽町駅",
        # "六本木駅",
    ]
    area_list = [[area1, area2] for area2 in area2s]

    media_type_obj = models.Media_type.objects.get(media_type=media_type)

    for area1, area2 in area_list:
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        dw = Wait_located(driver)
        print(area1 + " " + area2)

        area_obj = models.Area.objects.get(area_name=area1 + " " + area2)

        # driver = webdriver.Chrome('chromedriver', options=driver_settings.options)

        driver.get('https://www.ubereats.com/jp/')

        input_area = driver.find_element_by_id('location-typeahead-home-input')
        input_area.send_keys(f'{area1}{area2}')
        sleep(2)
        input_area.send_keys(Keys.ENTER)

        # 「最も人気の料理」ーーーーーーーーーー
        sleep(5)
        try:
            driver.find_element_by_xpath("//span[contains(text(), '並べ替え')]").click()
            driver.find_element_by_xpath("//span[contains(text(), '  最も人気の料理')]").click()
            # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()  # TOP画面用
        except Exception:
            driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()
            # dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()
            # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()  # ラジオボタン押下後の画面用 保険で

        # さらに表示ーーーーーーーーーー
        # next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
        while True:
            try:
                next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
                # next_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div[2]/div/button')))
                # sleep(1)
                next_btn.click()
            except Exception:
                break
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

        # def get_data():
        num = 1
        datalist = []
        switch = False

        try:
            while True:
                # for i in range(20):
                di = {}
                try:
                    driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{num}]/div/a/h3').click()
                except Exception:
                    break

                if switch is False:
                    try:
                        dw.wait_lacated_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/h1')
                    except TimeoutException:
                        switch = True
                if switch is True:
                    try:
                        dw.wait_lacated_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div[3]/div[1]/div[2]/div[2]/h1')
                    except TimeoutException:
                        dw.wait_lacated_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/h1')
                        switch = False

                try:
                    di["name"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/h1').text[:100]
                except NoSuchElementException:
                    try:
                        di["name"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div[3]/div[1]/div[2]/div[2]/h1').text[:100]
                    except Exception:
                        di["name"] = ""
                if "\"" in di["name"]:
                    di["name"].split("\"")[0].strip()
                elif "\'" in di["name"]:
                    di["name"].split("\'")[0].strip()

                # 飲食以外のワードならcontinue カラオケ等
                if [s for s in sub.OTHER_THAN_RESTAURANTS if re.match(s.replace(' ', '').replace('　', ''), di["name"].replace(' ', '').replace('　', ''))]:
                    print('飲食以外ネーム')
                    num += 1
                    sleep(2)
                    driver.back()
                    sleep(3)
                    continue

                try:
                    di["rate"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/div[1]/div[5]').text
                except NoSuchElementException:
                    try:
                        di["rate"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div[3]/div[1]/div[2]/div[2]/div[1]/div[1]').text
                    except Exception:
                        di["rate"] = None
                try:
                    di["review_count"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/div[1]/div[7]').text.replace('(', '').replace(')', '').replace('+', '')
                except NoSuchElementException:
                    try:
                        di["review_count"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div[3]/div[1]/div[2]/div[2]/div[1]/div[3]').text.replace('(', '').replace(')', '').replace('+', '')
                    except Exception:
                        di["review_count"] = None
                try:
                    di["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[4]/div/div[1]/p').text.split(',')[0].replace("さらに表示", "").strip()
                except Exception:
                    di["address"] = None
                di["url"] = driver.current_url[:1000]
                di["collected"] = datetime.datetime.now()

                print(f"count {num}")
                print(di["name"])
                print(di["rate"], di["review_count"], di["address"])
                print("\n")

                datalist.append(di)

                sleep(2)
                driver.back()
                sleep(3)
                num += 1

        except Exception as e:
            print(type(e), e)
            print("途中でエラーあり")

        driver.quit()

        # count = 1
        # elem = dw.wait_lacated_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{1}]/div/a/div/div[1]/p')

        # while elem:
        #     try:
        #         elem = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{count}]/div/a/div/div[1]/p')
        #     except NoSuchElementException:
        #         elem = None
        #         count -= 1
        #     else:
        #         count += 1

        # debug_list = []
        # datalist = []

        # for i in range(1, count + 1):
        #     dict = {}
        #     dict["name"] = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div[1]/p').text

        #     try:  # html構成がちょくちょくかわる
        #         dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[3]/div/span[1]').text)
        #     except (ValueError, NoSuchElementException):
        #         try:
        #             dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[2]/div/span[1]').text)
        #         except (ValueError, NoSuchElementException):
        #             dict["rate"] = 0

        #     try:  # html構成がちょくちょくかわる
        #         dict["review_count"] = int(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[3]/div/span[3]').text.replace("(", "").replace(")", "").replace("+", ""))
        #     except (ValueError, NoSuchElementException):
        #         try:
        #             dict["review_count"] = int(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[2]/div/span[3]').text.replace("(", "").replace(")", "").replace("+", ""))
        #         except (ValueError, NoSuchElementException):
        #             dict["review_count"] = 0

        #     dict["url"] = driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/figure/a').get_attribute('href')
        #     for k, v in dict.items():
        #         if not v:
        #             # debug(dict)
        #             print('取得結果が空です。')
        #             debug_list.append(dict)
        #             break

        #     datalist.append(dict)
        #     print(dict["store_name"])
        # # return datalist, debug_list

        # datalist, debug_list = get_data()

        # def create_ignoreList():
        #     area1_word = area1[:-1]
        #     area2_word = area2 if area1 == "東京都" else area2[:-1]
        #     ignore_list = [' ', area1_word, area2_word, "店", "個室", "居酒屋"]
        #     # ignore_listに英語も入れる
        #     tr = Translator()
        #     # del ignore_list[0] # 最初に入ってる空白を消す
        #     add_ignore = []
        #     for src in ignore_list:
        #         try:
        #             en_word = tr.translate(src, src='ja', dest='en').text.lower()
        #             add_ignore.append(en_word)
        #         except Exception as e:
        #             print(e)
        #     ignore_list += add_ignore
        #     ignore_list.append("store")
        #     return ignore_list
        # ignore_list = create_ignoreList()

        # created_list = []
        # atode_list = []

        # 一旦削除
        # models.Media_data.objects.filter(store__area=area_obj, media_type=media_type_obj).delete()

        # for store in datalist:
        #     atode_flg = False
        #     atode_dict = {}

        #     store_name = store["store_name"]
        #     rate = store["rate"]
        #     store_url = store["url"]
        #     review_count = store["review_count"]

        #     store_obj, _atode_flg, _atode_dict, _created_list = store_model_process(area_obj, media_type, store_name, ignore_list)

        #     atode_flg = _atode_flg
        #     atode_dict.update(_atode_dict)
        #     created_list += _created_list

        #     # media_data用ーーー
        #     if atode_flg is False:
        #         media_obj, _ = models.Media_data.objects.update_or_create(
        #             store=store_obj, media_type=media_type_obj,
        #             defaults={
        #                 "url": store_url,
        #                 "rate": rate,
        #                 "review_count": review_count,
        #             }
        #         )
        #     else:
        #         atode_dict["store_url"] = store_url
        #         atode_dict["rate"] = rate

        #     # # レビューカウント用
        #     # media_obj = models.Media_data.objects.get(store=store_obj, media_type=media_type_obj)
        #     # review_count = len(models.Review.objects.filter(media=media_obj))
        #     # if atode_flg is False:
        #     #     models.Media_data.objects.update_or_create(
        #     #         store=store_obj, media_type=media_type_obj, defaults={
        #     #             "review_count": review_count,
        #     #         }
        #     #     )

        #     # atode処理ーーーーーーーーー
        #     if atode_dict:
        #         atode_list.append(atode_dict)
        #     # ーーーーーーーーーーーー

        # except Exception as e:
        #     print(e)
        #     capture(driver)
        #     print(f'えらー {page_num} キャプチャ！')
        #     driver.quit()

        if datalist:
            generate_json(datalist, "uber", area1, area2, start_page=1, page_num=num)

        #     _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        #     created_list += _created_list
        #     print('不採用は、')
        #     pp(not_adopted_list)

        # if input('clean_store_objする？y/n: ') == "y":
        #     clean_store_obj(area_obj)

        # print('作成は、')
        # pp(created_list)
        # print('デバッグリスト、')
        # pp(debug_list)
