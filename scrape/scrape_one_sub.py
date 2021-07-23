from scrape import models
from time import sleep
import datetime
from site_packages.sub import name_set, address_set, category_set
from decimal import Decimal
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pytz

from devtools import debug
from pprint import pprint as pp
from dateutil.relativedelta import relativedelta

try:
    from my_module import capture, Wait_located
    from scrape_kit import generate_json, endpage_memo, address_ng_memo
except ImportError:
    from site_packages.my_module import Wait_located
    from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo


def scrape_one(driver, media, area1, area2, origin_name):
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    area_name = area1 + " " + area2
    media_type_obj = models.Media_type.objects.get(media_type=media)
    store_obj = models.Store.objects.get(store_name=origin_name, area__area_name=area_name)

    if media == "tb":
        handle_array = driver.window_handles
        driver.switch_to.window(handle_array[-1])
        sleep(0.5)
        print('handle OK!')

        store_name = driver.find_element_by_class_name('display-name').text
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

        print(store_name)
        print(yomi_roma)

    elif media == "google":
        store_name = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div > div > div > h2').text
        yomigana, yomi_roma = "", ""

    name_set(store_obj, store_name, media, yomigana=yomigana, yomi_roma=yomi_roma)

    if media == "tb":
        try:
            address = driver.find_element_by_class_name('rstinfo-table__address').text
            print(address)
        except Exception:
            address = ""
            print('住所取得NG')

    elif media == "google":
        import re
        # 全角→半角 変換
        ZEN = "".join(chr(0xff01 + i) for i in range(94))
        HAN = "".join(chr(0x21 + i) for i in range(94))
        ZEN2HAN = str.maketrans(ZEN, HAN)
        # HAN2ZEN = str.maketrans(HAN, ZEN)
        try:
            address: str = driver.find_element_by_xpath("//span[a[contains(text(),'所在地')]]/following-sibling::span").text
            zipcode = re.search("〒?\d{3}-\d{4}", address).group()
            address = address.replace(zipcode, "").replace("日本、", "").strip()
            # 全角→半角 変換
            address = address.translate(ZEN2HAN)
            print(address)
        except Exception:
            address = ""
            print('住所取得NG')

    address_set(store_obj, address, media)

    if media == "tb":
        try:
            category_list = driver.find_elements_by_class_name('rdheader-subinfo__item-text')[1].text.split('\n')
        except Exception:
            category_list = None
        # カテゴリ登録
        if category_list:
            category_set(store_obj, category_list)

    # try:
    #     phone: str = driver.find_elements_by_class_name('rstinfo-table__tel-num')[-1].text
    #     type(int(phone.replace('-', ''))) == int  # 電話番号が非公開がたまにある
    # except Exception:
    #     phone = ""

    # media_data用ーーー
    collected_date = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    if media == "tb":
        rate = driver.find_element_by_class_name('rdheader-rating__score-val-dtl').text
        rate: float = 0 if rate == '-' else float(rate)
        review_count = driver.find_element_by_class_name('rdheader-rating__review-target').find_element_by_tag_name('em').text
        review_count: int = 0 if review_count == '-' else int(review_count)

    elif media == "google":
        try:
            rate = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span').text
            rate: float = 0 if rate == '-' else float(rate)
        except Exception:
            rate = 0

        try:
            review_count = driver.find_element_by_xpath("//span[contains(text(),'Google のクチコミ')]").text
            review_count = int(review_count.split('（')[-1].replace('）', '').replace(',', ''))
        except Exception:
            print('no review_count')
            review_count = 0

    media_obj, _ = models.Media_data.objects.update_or_create(
        store=store_obj, media_type=media_type_obj,
        defaults={
            "collected": collected_date,
            "url": driver.current_url[:1000],
            "rate": rate,
            "review_count": review_count,
        }
    )

    all_md = models.Media_data.objects.filter(store=store_obj)
    # 店ごとのtotal_rate登録ーーーーー
    rate_md = [md for md in all_md if md.media_type.__str__() in ["gn", "google", "tb", "uber"]]
    rate_list, total_review_count = [], []
    for md in rate_md:
        if md.media_type.__str__() == "tb":  # 食べログ補正
            rate = md.rate + ((md.rate - Decimal("2.5")) * Decimal(".6"))
        else:
            rate = md.rate
        if md.review_count:
            rate_list.append(rate * md.review_count)
            total_review_count.append(md.review_count)
    try:
        total_rate = sum(rate_list) / sum(total_review_count)
    except ZeroDivisionError:
        total_rate = 0
    store_obj.total_rate = total_rate
    store_obj.save()

    # 店ごとのtotal_review_count登録ーーーーー
    rev_cnt_list = [md.review_count for md in all_md if md.review_count]
    try:
        total_review_count = sum(rev_cnt_list)
    except ZeroDivisionError:
        total_review_count = 0
    store_obj.total_review_count = total_review_count
    store_obj.save()

    # 口コミーーーーーーーーーー
    if media == "tb":
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
                        title = ""
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

                    print(review_date, content[:20])

                    rev_obj, _ = models.Review.objects.update_or_create(
                        media=media_obj, content=content
                    )

                    if title:
                        # 長さ制限
                        if len(title) > 100:
                            title = title[:100]
                        rev_obj.title = title
                    if review_date:
                        rev_obj.review_date = review_date
                    if review_point:
                        rev_obj.review_point = review_point
                    if log_num:
                        rev_obj.log_num_byTabelog = log_num

                    rev_obj.save()

                    print('レビュー登録!!')

        driver.execute_script("window.close();")

    elif media == "google":
        try:
            driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span:nth-child(3) > span > a').click()  # 口コミボタンクリック
            sleep(1.5)
        except Exception:
            print('口コミクリックエラー')

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
                    # else:
                    #     review_date = today + relativedelta(day=1)

                    # ポイント処理ーーーー
                    review_point = driver.find_element_by_css_selector(
                        f'div#reviewSort > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type({review_num}) > div:nth-of-type(1) > div:nth-of-type(3) > div > g-review-stars > span').get_attribute('aria-label')  # '5 点中 4.0 点の評価、'
                    splited = review_point.split(' ')
                    review_point = float(splited[2])

                    rev_obj, _ = models.Review.objects.update_or_create(
                        media=media_obj, content=content
                    )
                    try:
                        # 長さ制限
                        if len(title) > 100:
                            title = title[:100]
                        rev_obj.title = title
                    except Exception:
                        pass
                    if review_date:
                        rev_obj.review_date = review_date
                    if review_point:
                        rev_obj.review_point = review_point
                    try:
                        rev_obj.log_num_byTabelog = log_num
                    except Exception:
                        pass

                    rev_obj.save()

                    print('レビュー登録!!')

        # データ収集。新規順ボタンが押せない場合があるので2周する。
        collect_review()
        try:
            # driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(2) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
            driver.find_element_by_xpath("//div[span[contains(text(),'新規順')]]").click()  # 新規順クリック

            print('新規順クリック')
            collect_review()  # もう一回
            sleep(1)
        except Exception:
            try:
                driver.find_element_by_css_selector('div.review-dialog-list > div:nth-of-type(3) > g-scrolling-carousel > div > div > div:nth-of-type(2)').click()  # 新規順クリック
                print('新規順クリック')
                collect_review()  # もう一回
                sleep(1)
            except Exception:
                print('新規順クリックerror!!!!!!!!!')

        sleep(1)

        actions = webdriver.ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()  # 閉じる
