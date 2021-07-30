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
    from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo, duplicated_by_google_memo


from site_packages.my_module import collectStoreOtherThanThat


def scrape_google_refill():
    area1 = "千葉県"
    # area2 = "木更津市"
    # area2 = "習志野市"
    # area2 = "市川市"
    # area2 = "千葉市"
    area2 = "松戸市"

    # area1 = "埼玉県"
    # area2 = "上尾市"
    # area2 = "桶川市"
    # area2 = "熊谷市"
    # area2 = "浦和"

    area_name = area1 + " " + area2
    media = "google"

    print(area1, area2, media)

    # collectStoreOtherThanThatやったあとエラーになっても困るので先に開いとく
    # driver = webdriver.Chrome('chromedriver', options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版
    driver.get('https://google.com/?hl=ja')
    area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
    area_input.send_keys(f'{area_name} 飲食店' + Keys.ENTER)
    sleep(2)

    # google検索を引き続きご利用いただく前に、、、
    try:
        driver.find_element_by_xpath('//div[text()="同意する"]').click()
        sleep(2)
    except NoSuchElementException:
        pass
    driver.find_element_by_link_text('すべて表示').click()
    sleep(2)

    to_collect = collectStoreOtherThanThat(area_name, media)
    n = datetime.datetime.now()
    with open(f"/Users/yutakakudo/Google ドライブ/colab/json/refill_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
        for line in to_collect:
            f.write(f"{line}\n")
    # with open('/Users/yutakakudo/Google ドライブ/colab/json/refill_埼玉県_浦和_2021-07-28_1644.txt') as f:
    #     to_collect = [s.strip() for s in f.readlines()]
    # # to_collect[-735]
    # to_collect = to_collect[-820:]

    IGNORE_NAME_LIST = [
        "居酒屋",
        "タウンハウジング吉祥寺店",
        "丸広百貨店 上尾店",
        "イオンモール上尾",
        "シャポー船橋",
        "船橋フェイス",
        "東急プラザ 銀座",
        "マロニエゲート銀座1",
        "銀座三越",
        "銀座インズ1",
        "GINZA SIX",
        "東京ミッドタウン日比谷",
        "東京国際フォーラム",
        "日比谷グルメゾン",
        "日比谷OKUROJI",
        "東急プラザ 銀座",
        "銀座コア",
        "日比谷シティ国際ビル",
        "帝劇ビル",
        "日比谷シャンテ",
        "エキュートエディション有楽町",
        "有楽町産直横丁",
        "新東京ビル",
        "有楽町イトシア",
        "ルミネ 有楽町",
        "帝国ホテル 東京",
        "有楽町ビル",
        "東京交通会館",
        "デックス 東京ビーチ",
        "アクアシティお台場",
        "お台場たこ焼きミュージアム",
        "ヴィーナスフォート",
        "パレットタウン",
        "新中野駅",
        "中野サンプラザ",
        "中野マルイ",
        "1000円カット",
        "西武渋谷店",
        "グランベリーパーク",
        "ルミネ町田",
        "町田マルイ",
        "小田急マルシェ",
        "小田急百貨店 町田店",
        "レミィ町田",
        "町田モディ",
        "レストラン",
        "東京ミッドタウン",
        "松坂屋 上野店",
        "アトレ上野",
        "PC Fixs新宿高田馬場店",
        "ミニミニ高田馬場店",
        "タウンハウジング高田馬場店",
        "中野ブロードウェイ",
        "恵比寿ガーデンプレイスタワー",
        "アトレ恵比寿",
        "恵比寿横丁",
        "株式会社シンクロ・フード",
        "上野マルイ",
        "エミオ 練馬",
        "エミオ練馬高野台",
        "西友練馬店",
        "ホッピー通り",
        "EKIMISE 浅草",
        "浅草ROX",
        "浅草花やしき",
        "ハッピーロード大山",
        "ビーンズ 赤羽",
        "イトーヨーカドー 赤羽店",
        "ダイエー 赤羽店 ・イオンフードスタイル",
        "赤羽アピレ",
        "エキュート赤羽",
        "スーパーホテル東京・赤羽駅南口",
        "国分寺マルイ",
        "セレオ国分寺",
        "千日前本店",
        "坐・和民 国分寺南口店",
        "エディオンなんば本店",
        "GEMSなんば",
        "髙島屋 大阪店",
        "なんばCITY 本館",
        "なんばウォーク",
        "ビックカメラ なんば店",
        "道頓堀",
        "なんばパークス",
        "ホテルロイヤルクラシック大阪",
        "新宿ごちそうビル",
        "あべのキューズモール",
        "ミーツ 国分寺",
        "なんばこめじるし",
        "心斎橋PARCO",
        "大丸心斎橋店",
        "アローホテルイン心斎橋",
        "アメリカ村",
        "アルモニーアンブラッセ ウェディングホテル",
        "ホテルマイステイズ心斎橋",
        "ホテル日航大阪",
        "アルバータ・アルバータ",
        "",
        "",
        "",
        "",
    ]

    # 全角→半角 変換
    ZEN = "".join(chr(0xff01 + i) for i in range(94))
    HAN = "".join(chr(0x21 + i) for i in range(94))
    ZEN2HAN = str.maketrans(ZEN, HAN)
    # HAN2ZEN = str.maketrans(HAN, ZEN)

    atode_list = []
    # created_list = []
    # duplicated_list = []

    address_ng_list = []

    debug_list = []

    length = len(to_collect)

    try:
        for st_name in to_collect:

            print(f'あと {length}')
            search_window = driver.find_element_by_xpath("//input[@aria-label='検索']")
            search_window.clear()
            sleep(0.5)
            # search_window.send_keys(f"{area_name} asobi")
            search_window.send_keys(f"{area_name} 飲食店 {st_name}")
            search_window.submit()

            sleep(1.5)

            atode_dict = {}

            # 広告枠とばしーーーーーーーーー
            details_class = driver.find_elements_by_xpath("//span[contains(@class,'__details')]")
            ad_count = 0
            for c in details_class:
                try:
                    if c.text.count('広告'):
                        ad_count += 1
                except Exception as e:
                    print(type(e), e)
                    print('広告カウントでエラー？')
            print("ad_count: " + str(ad_count))

            try:
                driver.find_element_by_css_selector(f'div.rl_full-list > div > div > div > div:nth-child(4) > div:nth-child({1+ad_count})').click()
                sleep(2)
            except Exception:
                length -= 1
                print('店選択エラー continue')
                continue

            try:
                store_name = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div > div > div > h2').text
            except Exception:
                length -= 1
                print('store_name取得エラー continue')
                continue

            if store_name in IGNORE_NAME_LIST or re.match(".*駅$", store_name):  # 多分Googleだけ、変な名前や施設名
                length -= 1
                print('IGNORE_NAME_LIST continue')
                continue

            atode_dict["name"] = store_name
            atode_dict["origin_name"] = st_name
            debug(st_name)
            debug(store_name)

            try:
                phone = driver.find_element_by_xpath('/html/body/div[6]/div/div[8]/div[2]/div/div[2]/async-local-kp/div/div/div[1]/div/div/div/div[1]/div/div[1]/div').find_element_by_xpath("//span[@role='link']").text
                type(int(phone.replace('-', ''))) == int  # 電話番号が非公開がたまにある
                debug(phone)
            except Exception:
                print('no phone!')
                phone = None
            atode_dict["phone"] = phone

            try:
                address = driver.find_element_by_xpath("//span[a[contains(text(),'所在地')]]/following-sibling::span").text
                zipcode = re.search("〒?\d{3}-\d{4}", address).group()
                address = address.replace(zipcode, "").replace("日本、", "").strip()
                # 全角→半角 変換
                address = address.translate(ZEN2HAN)
                print(address)
            except Exception:
                address_ng_list.append(store_name)
                address = ""
                print('住所取得NG')
            atode_dict["address"] = address

            # media_data用ーーー
            collected_date = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

            try:
                rate = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span').text
                rate: float = 0 if rate == '-' else float(rate)
            except Exception:
                rate = 0

            try:
                rev_count = driver.find_element_by_xpath("//span[contains(text(),'Google のクチコミ')]").text
                rev_count = int(rev_count.split('（')[-1].replace('）', '').replace(',', ''))
            except Exception:
                print('no rev_count')
                rev_count = 0

            atode_dict["collected"] = collected_date
            atode_dict["url"] = driver.current_url
            atode_dict["rate"] = rate
            atode_dict["review_count"] = rev_count

            atode_review_list = []
            no_review_flg = False
            try:
                driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span:nth-child(3) > span > a').click()  # 口コミボタンクリック
                sleep(1)
            except Exception:
                print('口コミクリックなし or エラー')
                # length -= 1
                # continue
                no_review_flg = True

            def collect_review():
                sleep(2)
                for review_num in range(1, 6):
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

                    if content:

                        # 日付け処理ーーーーー
                        review_date = driver.find_element_by_css_selector(f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div > span:nth-of-type(1)').text
                        splited = review_date.split(' ')
                        today = datetime.datetime.today()
                        if splited[1] == "時間前":
                            review_date = (today - relativedelta(hours=int(splited[0]))) + relativedelta(day=1)
                        elif splited[1] == "日前":
                            review_date = (today - relativedelta(days=int(splited[0]))) + relativedelta(day=1)
                        elif splited[1] == "週間前":
                            review_date = (today - relativedelta(weeks=int(splited[0]))) + relativedelta(day=1)
                        elif splited[1] == "か月前":
                            review_date = (today - relativedelta(months=int(splited[0]))) + relativedelta(day=1)
                        elif splited[1] == "年前":
                            review_date = (today - relativedelta(years=int(splited[0]))) + relativedelta(day=1)
                        else:
                            debug_list.append(store_name)
                            debug_list.append(review_date)
                            debug_list.append(content)
                            review_date = today + relativedelta(day=1)

                        # ポイント処理ーーーー
                        review_point = driver.find_element_by_css_selector(
                            f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div > g-review-stars > span').get_attribute('aria-label')  # '5 点中 4.0 点の評価、'
                        splited = review_point.split(' ')
                        review_point = float(splited[2])

                        # {"name in name_list:":a,"name in name_list:":a,"phone":a,"url":a,"rate":a,
                        # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                        atode_review_dict = {}
                        atode_review_dict["content"] = content
                        atode_review_dict["date"] = review_date
                        atode_review_dict["review_point"] = review_point
                        atode_review_list.append(atode_review_dict)

            if not no_review_flg:
                # データ収集。新規順ボタンが押せない場合があるので2周する。
                collect_review()
                try:
                    # driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(2) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
                    driver.find_element_by_xpath("//div[span[contains(text(),'新規順')]]").click()  # 新規順クリック

                    print('新規順クリック')
                    collect_review()  # もう一回
                    # sleep(1)
                except Exception:
                    try:
                        driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(3) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
                        print('新規順クリック')
                        collect_review()  # もう一回
                        # sleep(1)
                    except Exception:
                        print('新規順クリックerror!!!!!!!!!')


                # driver.find_element_by_xpath(f'/html/body/span[{store_num}]/g-lightbox/div[2]/div[2]').click() # 閉じるボタン
                actions = webdriver.ActionChains(driver)
                actions.send_keys(Keys.ESCAPE).perform()  # 閉じる

                
            atode_dict["review"] = atode_review_list

            atode_list.append(atode_dict)

            # # 重複したものを抜粋ーーーーーーー
            # if store_name in created_list:
            #     duplicated_list.append(store_name)
            #     duplicated_list.append(st_name)
            #     duplicated_list.append(" \n")

            # created_list.append(store_name)

            sleep(2)
            length -= 1

    except Exception as e:
        print(type(e), e)
        print('｜｜｜｜中断｜｜｜｜')
        capture(driver)
        print('capture撮影！！')

    if atode_list:
        generate_json(atode_list, media, area1, area2)

    if address_ng_list:
        address_ng_memo(address_ng_list, media, area1, area2)

    # if duplicated_list:
    #     duplicated_by_google_memo(duplicated_list, area1, area2)

    driver.quit()
