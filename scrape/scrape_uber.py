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
options.add_argument('--blink-settings=imagesEnabled=false')  # ç»ćăȘă
options.add_argument('--no-sandbox')
# options.binary_location = '/usr/bin/google-chrome'
options.add_argument('--proxy-bypass-list=*')      # ăăčăŠăźăăčăć
options.add_argument('--proxy-server="direct://"')  # Proxyç”ç±ă§ăŻăȘăçŽæ„æ„ç¶ăă
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
    word = word.replace(' ', '').replace('ă', '')
    return word.isalnum()


def scrape_uber():

    # area1 = "ćèç"
    # area2s = [
    #     # "èčæ©ćž",
    #     # "ćžć·ćž",
    #     # "ćèćž",
    #     # "æćž",

    #     # "æŸæžćž",
    #     # "éć­ćž",
    #     # "é€šć±±ćž",
    #     # "çżćżéćž",
    #     "æšæŽæŽ„ćž",
    #     # "",
    # ]
    area1 = "æ±äșŹéœ"
    area2s = [
        # "éć±±äžäžçźé§",
        # "è”€çŸœé§",
        # "ç§èćé§",
        # "æ”èé§",
        # "éș»ćžćçȘé§",
        "æ± èąé§",
        "æżæ©é§",
        "äžéé§",
        # "æ”æŻćŻżé§",
        # "ć€§äčäżé§",
        # "ăć°ć Žæ”·æ”ćŹćé§",
        # "ććäœé§",
        # "ćç„„ćŻșé§",
        # "éćș§é§",
        # "ćœććŻșé§",
        # "äžè»è¶ć±é§",
        # "æžè°·é§",
        # "æ°ćźżé§",
        # "æ°æ©é§",
        # "èȘç±ăäžé§",
        # "æ°Žéæ©é§",
        # "é«ç°éŠŹć Žé§",
        # "äž­éé§",
        # "äž­çźé»é§",
        # "æ„æŹæ©é§",
        # "ç·ŽéŠŹé§",
        # "ććźżé§",
        # "äșć­çć·é§",
        # "çșç°é§",
        # "ææ„œçșé§",
        # "ć­æŹæšé§",
    ]
    area_list = [[area1, area2] for area2 in area2s]

    for area1, area2 in area_list:
        # driver = webdriver.Chrome('chromedriver', options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        dw = Wait_located(driver)  # èȘäœăźWebDriverWaitç°Ąæœç
        print(area1 + " " + area2)

        # driver = webdriver.Chrome('chromedriver', options=driver_settings.options)

        driver.get('https://www.ubereats.com/jp/')

        input_area = driver.find_element_by_id('location-typeahead-home-input')
        input_area.send_keys(f'{area1}{area2}')
        sleep(2)
        input_area.send_keys(Keys.ENTER)

        # ăæăäșșæ°ăźæçăăŒăŒăŒăŒăŒăŒăŒăŒăŒăŒ
        sleep(5)
        try:
            driver.find_element_by_xpath("//span[contains(text(), 'äžŠăčæżă')]").click()
            driver.find_element_by_xpath("//span[contains(text(), '  æăäșșæ°ăźæç')]").click()
            # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()  # TOPç»éąçš
        except Exception:
            driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/div/label[2]/span').click()
            # dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()
            # driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/label[2]/span').click()  # ă©ăžăȘăăżăłæŒäžćŸăźç»éąçš äżéșă§

        # ăăă«èĄšç€șăŒăŒăŒăŒăŒăŒăŒăŒăŒăŒ
        # next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
        while True:
            try:
                sleep(5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # ăăăȘăăšèȘ­ăăȘă

                next_btn = dw.wait_lacated_xpath('/html/body/div[1]/div/main/div/div/div[2]/div/button')
                # next_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div/div/div[2]/div/button')))
                # sleep(1)
                next_btn.click()
            except Exception:
                break
            print("next_btn")

        # res = driver.page_source
        # soupæł
        # soup = BeautifulSoup(res, 'html.parser')
        # ćšäœăćăăăăçčæ°ă€ăăŠăȘăćșăăăŁăăăăăăăăæ°çăăȘăOKă§ăăŒăŒăŒăŒăŒăŒ
        # store_names = [n.text for n in soup.select('.h3.cq.ce.cp.an.al.m0.bu')]
        # store_names = [n.text for n in soup.select('.be.bf.bg.g2.an.al.kc.bh')] #ăă¶ăăäžćźæéă§ăŻă©ăčćć€ăăăăčăŻăŹă€ăăłă°ćŻŸç­ă
        # rate = [n.text for n in soup.select('div.gt.cd.ce.ec.eb.iu')]
        # debug(list(zip(store_names,rate)))
        # len(store_names)
        # len(rate)

        # driveræł

        # def get_data():
        num = 1
        datalist = []
        switch = False

        try:
            while True:
                # for i in range(20):
                di = {}

                # ć­ćšçąșèȘ
                try:
                    dw.wait_lacated_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{num}]/div/a/h3')
                except Exception:
                    break

                # ăŹăŒăăăă
                # æłšæăhtmlæ§æăăĄăăăĄăăăăă
                if not driver.find_elements_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{num}]/div/div/div/div[2]/div[1]/div[3]') and not driver.find_elements_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{num}]/div/div/div/div[2]/div[1]/img'):
                    num += 1
                    print("ăŹăŒăăȘă")
                    continue

                # ćșăŻăȘăăŻ
                dw.wait_lacated_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{num}]/div/a/h3').click()

                # çŸćšć¶æ„­ăăŠăăă©ăăă§xpathăć€ăă wait_locatedă§xpathçąșèȘ
                if switch is False:
                    try:
                        dw.wait_lacated_xpath('//*[@id="main-content"]/div[3]/div/div[3]/div[3]/div[1]/div[2]/div[2]/h1')
                    except Exception:
                        switch = True
                if switch is True:
                    try:
                        dw.wait_lacated_xpath('//*[@id="main-content"]/div[3]/div/div[4]/div[3]/div[1]/div[2]/div[2]/h1')
                    except Exception:
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

                # éŁČéŁä»„ć€ăźăŻăŒăăȘăcontinue ă«ă©ăȘă±ç­
                if [s for s in sub.OTHER_THAN_RESTAURANTS if re.match(s.replace(' ', '').replace('ă', ''), di["name"].replace(' ', '').replace('ă', ''))]:
                    print('éŁČéŁä»„ć€ăăŒă ')
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
                    di["address"] = driver.find_element_by_xpath('//*[@id="main-content"]/div[4]/div/div[1]/p').text.split(',')[0].replace("ăăă«èĄšç€ș", "").strip()
                except Exception:
                    di["address"] = None
                di["url"] = driver.current_url[:1000]
                di["collected"] = datetime.datetime.now()

                print(f"count {num}")
                print(di["name"])
                print(di["rate"], di["review_count"], di["address"])
                print("")

                datalist.append(di)

                sleep(2)
                driver.back()
                sleep(3)
                num += 1

        except Exception as e:
            print(type(e), e)
            print("éäž­ă§ăšă©ăŒăă")

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

        # try:  # htmlæ§æăăĄăăăĄăăăăă
        #     dict["rate"] =
        #     float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/div/div/div[2]/div[1]/div[3]').text)
        #     driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/div/div/div[2]/div[1]/img')
        # except (ValueError, NoSuchElementException):
        #     try:
        #         dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[3]/div/span[1]').text)

        #     except (ValueError, NoSuchElementException):
        #         try:
        #             dict["rate"] = float(driver.find_element_by_xpath(f'/html/body/div[1]/div/main/div/div/div[2]/div/div[2]/div[{i}]/div/a/div/div/div/div[2]/div/span[1]').text)
        #         except (ValueError, NoSuchElementException):
        #             dict["rate"] = 0

        #     try:  # htmlæ§æăăĄăăăĄăăăăă
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
        #             print('ććŸç”æăç©șă§ăă')
        #             debug_list.append(dict)
        #             break

        #     datalist.append(dict)
        #     print(dict["store_name"])
        # # return datalist, debug_list

        # datalist, debug_list = get_data()

        # def create_ignoreList():
        #     area1_word = area1[:-1]
        #     area2_word = area2 if area1 == "æ±äșŹéœ" else area2[:-1]
        #     ignore_list = [' ', area1_word, area2_word, "ćș", "ććź€", "ć±éć±"]
        #     # ignore_listă«è±èȘăć„ăă
        #     tr = Translator()
        #     # del ignore_list[0] # æćă«ć„ăŁăŠăç©șçœăæ¶ă
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

        # äžæŠćé€
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

        # except Exception as e:
        #     print(e)
        #     capture(driver)
        #     print(f'ăăăŒ {page_num} ă­ăŁăăăŁïŒ')
        #     driver.quit()

        if datalist:
            generate_json(datalist, "uber", area1, area2, start_page=1, page_num=num)

        #     _created_list, not_adopted_list = atode_process(atode_list, media_type, media_type_obj, area_obj)

        #     created_list += _created_list
        #     print('äžæĄçšăŻă')
        #     pp(not_adopted_list)

        # if input('clean_store_objăăïŒy/n: ') == "y":
        #     clean_store_obj(area_obj)

        # print('äœæăŻă')
        # pp(created_list)
        # print('ăăăă°ăȘăčăă')
        # pp(debug_list)
