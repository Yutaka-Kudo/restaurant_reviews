from selenium import webdriver

# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup

import datetime
from devtools import debug
from pprint import pprint as pp

import json

from scrape.driver_settings import  options

# from my_module import capture, Wait_located
from site_packages.my_module import capture, Wait_located

area1 = "千葉県"
# area2 = "船橋市"
# area2 = "市川市"
# area2 = "千葉市"
area2 = "松戸市"

# area1 = "東京都"
# area2 = ""
# area2 = ""

# area1 = "埼玉県"
# area2 = "さいたま市"
# area2 = "上尾市"

# page_range = range(1,10)
page_range = range(10,20)
# page_range = range(1,20)
# page_range = range(20,40

media = "tb"


driver = webdriver.Chrome('chromedriver', options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版
driver.get('https://tabelog.com/')

area_input = driver.find_element_by_id('sa')
area_input.send_keys(f'{area2}' + Keys.ENTER)
sleep(2)

atode_list = []
created_list = []

# try:
for page_num in page_range:
    print(f'ペーーーじーーーーーー{page_num}')
    try:
        driver.find_element_by_xpath(f'//a[@class="c-pagination__num" and text()="{page_num}"]').click()  # ページ
    except Exception:
        pass

    dw.wait_lacated_class_name('list-rst__rst-name-target')  # 最初のelementが現れるまで待つ
    store_link_list = driver.find_elements_by_class_name('list-rst__rst-name-target')

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
        atode_dict["name"] = store_name
        print(store_name)

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
        store_url = driver.current_url
        rate = driver.find_element_by_class_name('rdheader-rating__score-val-dtl').text
        rate: float = 0 if rate == '-' else float(rate)
        review_count = driver.find_element_by_class_name('rdheader-rating__review-target').find_element_by_tag_name('em').text
        review_count: int = 0 if review_count == '-' else int(review_count)

        atode_dict["url"] = store_url
        atode_dict["rate"] = rate
        atode_dict["review_count"] = review_count

        # 口コミーーーーーーーーーー
        no_review_flg = False
        try:  # 口コミボタンが無い店もある
            driver.find_element_by_class_name('rstdtl-top-rvwlst__more-link').find_element_by_class_name('c-link-circle').click()
            sleep(1)
        except NoSuchElementException:
            no_review_flg = True
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
                except IndexError:
                    try:  # タイトルが無い投稿は本文の先頭24文字をとる。
                        title = content_wrap.select('.rvw-item__rvw-comment')[0].text.strip()[:24] + "…"
                    except IndexError:  # 本文もない場合はpass
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
                    print(content)

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

        driver.execute_script("window.close();")
        driver.switch_to.window(handle_array[0])
        sleep(1)


def date_trans_json(obj):
    if isinstance(obj,datetime.datetime):
        return obj.strftime('%Y-%m-%d')

n = datetime.datetime.now() + datetime.timedelta(hours=9)
with open(f"/content/drive/MyDrive/colab/json/{media}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.json","w") as f:
    json.dump(atode_list, f, indent=4, default=date_trans_json)


# except Exception as e:
#     print(type(e))
#     print(e)
#     print(f'えらー {page_num} キャプチャ！')
# capture(driver)
#     driver.quit()
#     raise Exception()

driver.quit()
