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
import pytz

import re


from selenium import webdriver
import random


def scrape_tb():

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-dev-shm-usage')

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

    # from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import NoSuchElementException
    from time import sleep
    from bs4 import BeautifulSoup

    import datetime
    import pytz
    from devtools import debug
    from pprint import pprint as pp

    import json

    # from scrape import driver_settings

    try:
        from my_module import capture, Wait_located
        from scrape_kit import generate_json, endpage_memo, address_ng_memo
    except ImportError:
        from site_packages.my_module import capture, Wait_located
        from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo

    area1 = "千葉県"
    area2s = [
        # "船橋市",
        # "市川市",
        # "千葉市",
        "柏市",
        # "松戸市",
        # "銚子市",
        # "館山市",
        # "",
        # "",
        # "",
    ]

    # area1 = "東京都"
    # area2s = [
    #     # "中目黒",
    #     "新宿",
    #     # "渋谷",
    #     # "吉祥寺",
    #     # "銀座",
    #     # "新橋",
    #     # "六本木",
    #     # "大久保",
    #     # "池袋",
    #     # "有楽町",
    #     # "日本橋",
    #     # "お台場",
    #     # "中野",
    #     # "北千住",
    #     # "町田",
    #     # "高田馬場",
    #     # "上野",
    #     # "浅草",
    #     # "恵比寿",
    #     # "練馬",
    #     # "板橋",
    #     # "赤羽",
    #     # "国分寺",
    #     # "麻布十番",
    #     # "原宿",
    #     # "青山一丁目",
    #     # "秋葉原",

    #     # "水道橋",
    #     # "自由が丘",
    #     # "三軒茶屋",
    #     # "二子玉川",
    #     # "錦糸町",
    #     # "押上",
    #     # "新小岩",
    #     # "蒲田",
    #     # "立川",
    #     # "八王子",
    #     # "新小岩",
    #     # "神楽坂",
    #     # "巣鴨",
    #     # "品川",
    #     # "五反田",
    #     # "大崎",
    #     # "下北沢",
    #     # "明大前",
    #     # "人形町",
    #     # "門前仲町",
    #     # "葛西",
    #     # "府中",
    #     # "調布",
    # ]

    # area1 = "埼玉県"
    # area2s = [
    #     # "さいたま市",
    #     # "上尾市",
    #     # "桶川市",
    #     "大宮",
    #     # "浦和",
    #     # "越谷市",
    #     # "",
    # ]

    # area1 = "大阪府"
    # area2s = [
    #     # "梅田",
    #     # "難波",
    #     # "心斎橋",
    #     # "天王寺",
    #     "本町",
    #     "鶴橋",
    #     # "",
    #     # "",
    #     # "",
    #     # "",
    #     # "",
    #     # "",
    #     # "",
    # ]

    # area1 = "神奈川県"
    # area2s = [
    #     # "横浜市",
    #     "鎌倉市",
    #     "川崎市",
    #     # "小田原市",
    #     # "藤沢市",
    #     # "茅ヶ崎市",
    #     # "平塚市",
    #     # "厚木市",
    #     # "海老名市",
    #     # "横須賀市",
    #     # "",
    #     # "",
    #     # "",
    # ]

    area_list = []
    for area2 in area2s:
        area_list.append([area1, area2])

    # page_range = range(1,20)
    # page_range = range(20,40)
    # page_range = range(1,30)
    # page_range = range(30,60)

    # page_range = range(1,3)

    range_list = [
        range(1, 30),
        range(30, 61),
        # range(1, 30),
        # range(1, 21),
        # range(21, 41),
    ]

    media = "tb"

    OTHER_THAN_RESTAURANTS = [
        "ファミリーマート",
        "ニューデイズ",
        "ピザハット",
        "デイリーヤマザキ",
        "ヤオコー",
        # "",
        # "",
        # "",
        # "",
        # "",
    ]

    alias_dict = {
        "麻布": "麻布十番",
        "青山": "青山一丁目",
        # "" : "",
        # "" : "",
        # "" : "",
        # "" : "",
        # "" : "",
    }

    # driver = webdriver.Chrome('chromedriver', options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    for area1, area2 in area_list:

        # page_rangeをわけてある
        for page_range in range_list:

            driver.get('https://tabelog.com/')

            # 思った通りの第一候補が取れない際
            try:
                area2alias = alias_dict[area2]
            except KeyError:
                area2alias = area2
            print(f'area2alias {area2alias}')

            area_input = driver.find_element_by_id('sa')
            if area1 == "東京都":
                area_input.send_keys(f'{area2alias}駅' + Keys.ENTER)
            else:
                area_input.send_keys(f'{area2alias}' + Keys.ENTER)
            sleep(2)

            start_page = list(page_range)[0]

            atode_list = []
            address_ng_list = []

            already_list = []

            page_end_flg = False

            page_range = list(page_range)
            # 大きいページ番号からスタートの際のページ送り
            try:
                if page_range[0] >= 5:
                    page_num = 5
                    while page_range[0] > page_num:
                        driver.find_element_by_xpath(f'//a[@class="c-pagination__num" and text()="{page_num}"]').click()  # ページ
                        print(f'ページ移動中...{page_num}')
                        sleep(2)
                        page_num += 1
            except NoSuchElementException as e:
                print(type(e), e)
                page_end_flg = True
            except Exception as e:
                print(type(e), e)
                print('ページ遷移エラー')
                raise Exception(e)

            # try:
            if page_end_flg is False:
                for page_num in page_range:
                    print(' ')
                    print(f'ペーーーじーーーーーー{page_num}')
                    if page_num != 1:
                        try:
                            driver.find_element_by_xpath(f'//a[@class="c-pagination__num" and text()="{page_num}"]').click()  # ページ
                        except Exception:
                            page_end_flg = True
                            break

                    dw.wait_lacated_class_name('list-rst__rst-name-target')  # 最初のelementが現れるまで待つ
                    store_link_list = driver.find_elements_by_class_name('list-rst__rst-name-target')
                    # store_link_list = driver.find_elements_by_class_name('list-rst__rst-name-target')[:3]
                    for elem in store_link_list:
                        atode_flg = False
                        atode_dict = {}

                        # try:  # よくここでつまづく
                        driver.execute_script("window.scrollTo(0, 0);")  # これないと読めないときもある

                        elem.click()

                        # except Exception:
                        #     capture(driver)
                        #     raise Exception()

                        # webdriver.ActionChains(driver).key_down(Keys.COMMAND).click(elem).perform() # なぜかこれで新規タブで開くと、次の普通クリックでも新規タブが開く
                        sleep(2)

                        handle_array = driver.window_handles
                        driver.switch_to.window(handle_array[-1])
                        sleep(0.5)
                        print('handle OK!')

                        # store_name = driver.find_element_by_class_name('display-name').text
                        store_name = dw.wait_lacated_class_name('display-name').text

                        # 絶対飲食以外のワードならcontinue カラオケ等
                        if [s for s in OTHER_THAN_RESTAURANTS if s in store_name]:
                            driver.execute_script("window.close();")
                            driver.switch_to.window(handle_array[0])
                            sleep(1)
                            continue

                        # かぶり店
                        if store_name in already_list:
                            print('かぶりスキップ！')
                            driver.execute_script("window.close();")
                            driver.switch_to.window(handle_array[0])
                            sleep(1)
                            continue

                        atode_dict["name"] = store_name
                        print(store_name)

                        try:
                            alias_name: str = driver.find_element_by_class_name('alias').text.replace("）", "").replace("（", "").replace(" ", "").replace("　", "")
                            if alias_name.isascii() and alias_name != "":
                                yomi_roma = alias_name
                                yomigana = ""
                            else:
                                yomigana = alias_name
                                yomi_roma = ""
                        except Exception:
                            yomigana = ""
                            yomi_roma = ""
                        atode_dict["yomigana"] = yomigana
                        atode_dict["yomi_roma"] = yomi_roma

                        try:
                            address = driver.find_element_by_class_name('rstinfo-table__address').text
                            print(address)
                        except Exception:
                            address_ng_list.append(store_name)
                            address = ""
                            print('住所取得NG')
                        atode_dict["address"] = address

                        try:
                            category_list = driver.find_elements_by_class_name('rdheader-subinfo__item-text')[1].text.split('\n')
                        except Exception:
                            category_list = None
                        atode_dict["category"] = category_list

                        try:
                            phone: str = driver.find_elements_by_class_name('rstinfo-table__tel-num')[-1].text
                            type(int(phone.replace('-', ''))) == int  # 電話番号が非公開がたまにある
                        except Exception:
                            phone = ""
                        atode_dict["phone"] = phone

                        # debug(store_name, phone)

                        # media_data用ーーー
                        collected_date = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
                        rate = driver.find_element_by_class_name('rdheader-rating__score-val-dtl').text
                        rate: float = 0 if rate == '-' else float(rate)
                        review_count = driver.find_element_by_class_name('rdheader-rating__review-target').find_element_by_tag_name('em').text
                        review_count: int = 0 if review_count == '-' else int(review_count)

                        atode_dict["collected"] = collected_date
                        atode_dict["url"] = driver.current_url
                        atode_dict["rate"] = rate
                        atode_dict["review_count"] = review_count

                        # 口コミーーーーーーーーーー
                        try:  # 口コミボタンが無い店もある
                            driver.find_element_by_class_name('rstdtl-top-rvwlst__more-link').find_element_by_class_name('c-link-circle').click()
                            sleep(1)
                        except NoSuchElementException:
                            print('口コミがありません。')
                        else:
                            dw.wait_lacated_link_text('訪問月順').click()
                            sleep(1)
                            print('口コミ発見！！')

                            # 「もっと見る」を全て展開ーーーーーーーー
                            mottomiru_list = driver.find_elements_by_class_name('js-show-review-items')[:6]  # 範囲制限
                            for i in mottomiru_list:
                                i.click()
                                sleep(0.6)  # 早すぎるとバグる
                            sleep(1)
                            res = driver.page_source
                            soup = BeautifulSoup(res, 'html.parser')
                            items = soup.select('div.js-rvw-item-clickable-area')[:5]  # 範囲制限
                            atode_review_list = []
                            for i, item in enumerate(items):  # 再訪は無視
                                no_data_flg = False
                                log = item.select('.rvw-item__rvwr-balloon-text')[0]
                                log_num = int(log.text.replace(',', '').replace('ログ', ''))
                                content_wrap = item.select_one('.rvw-item__review-contents-wrap')
                                try:
                                    title = content_wrap.select('.rvw-item__title')[0].text.strip()
                                except Exception:
                                    try:  # タイトルが無い投稿は本文の先頭24文字をとる。
                                        title = content_wrap.select('.rvw-item__rvw-comment')[0].text.strip()[:24] + "…"
                                    except Exception:  # 本文もない場合はpass
                                        no_data_flg = True
                                        print('no data!!')
                                try:
                                    review_point = item.select_one('.c-rating-v2__val.c-rating-v2__val--strong.rvw-item__ratings--val').get_text(strip=True)
                                    review_point = float(review_point)
                                except Exception:  # 評価値がついてない場合は0で入れるので、その後の表示等の処理を注意
                                    review_point = 0

                                if no_data_flg is False:
                                    content = item.select('.rvw-item__rvw-comment')[0]
                                    # <br>タグを\nに置き換える
                                    [s.replace_with('\n') for s in content.select('br')]
                                    # content = content.text.replace('\u200b', '').replace('\u3000', '').strip()
                                    content = content.text.strip()
                                    # print(content)

                                    try:  # 日時が「行った 〜〜」とあるときがある。
                                        for date_elem in item.select('div.rvw-item__single-date'):
                                            review_date = date_elem.get_text(strip=True)[:-2]
                                            review_date = datetime.datetime.strptime(review_date, '%Y/%m')
                                            break
                                    except ValueError:
                                        review_date = None

                                    # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                                    # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                                    atode_review_dict = {}
                                    atode_review_dict["title"] = title
                                    atode_review_dict["content"] = content
                                    atode_review_dict["date"] = review_date
                                    atode_review_dict["log_num"] = log_num
                                    atode_review_dict["review_point"] = review_point
                                    atode_review_list.append(atode_review_dict)

                            atode_dict["review"] = atode_review_list

                        atode_list.append(atode_dict)

                        # かぶり店
                        already_list.append(store_name)

                        driver.execute_script("window.close();")
                        driver.switch_to.window(handle_array[0])
                        sleep(1)

            if atode_list:
                generate_json(atode_list, media, area1, area2, start_page, page_num)

            if page_end_flg:
                endpage_memo(media, area1, area2, page_num)

            if address_ng_list:
                address_ng_memo(address_ng_list, media, area1, area2)

    # except Exception as e:
    #     print(type(e))
    #     print(e)
    #     print(f'えらー {page_num} キャプチャ！')
    # capture(driver)
    #     driver.quit()
    #     raise Exception()

    driver.quit()
