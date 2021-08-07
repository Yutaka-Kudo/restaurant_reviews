from time import sleep
import importlib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

from devtools import debug
from pprint import pprint as pp
from dateutil.relativedelta import relativedelta

from scrape import driver_settings, models

import random
import pyperclip
from glob import glob
from send2trash import send2trash

from scrape import scrape_one_sub

# options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--disable-dev-shm-usage')


# driver = webdriver.Chrome('chromedriver', options=options)
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)

import importlib
importlib.reload(driver_settings)

alias_dict = {
    "麻布": "麻布十番",
    "青山": "青山一丁目",
    # "" : "",
    # "" : "",
    # "" : "",
    # "" : "",
    # "" : "",
}

area1 = "千葉県"

area2 = "船橋市"
area2 = "市川市"
area2 = "千葉市"
area2 = "習志野市"
area2 = "松戸市"
area2 = "銚子市"
area2 = "館山市"
area2 = ""
area2 = ""
area2 = ""


area1 = "東京都"

area2 = "青山一丁目駅",
area2 = "赤羽駅",
area2 = "秋葉原駅",
area2 = "浅草駅",
area2 = "麻布十番駅",
area2 = "池袋駅",
area2 = "板橋駅",
area2 = "上野駅",
area2 = "恵比寿駅",
area2 = "大久保駅",
area2 = "お台場海浜公園駅",
area2 = "北千住駅",
area2 = "吉祥寺駅",
area2 = "銀座駅",
area2 = "国分寺駅",
area2 = "三軒茶屋駅",
area2 = "渋谷駅",
area2 = "新宿駅",
area2 = "新橋駅",
area2 = "自由が丘駅",
area2 = "水道橋駅",
area2 = "高田馬場駅",
area2 = "中野駅",
area2 = "中目黒駅",
area2 = "日本橋駅",
area2 = "練馬駅",
area2 = "原宿駅",
area2 = "二子玉川駅",
area2 = "町田駅",
area2 = "有楽町駅",
area2 = "六本木駅",

area2 = "錦糸町",
area2 = "押上",
area2 = "新小岩",
area2 = "蒲田",
area2 = "立川",
area2 = "八王子",
area2 = "新小岩",
area2 = "神楽坂",
area2 = "巣鴨",
area2 = "品川",
area2 = "五反田",
area2 = "大崎",
area2 = "下北沢",
area2 = "明大前",
area2 = "人形町",
area2 = "門前仲町",
area2 = "葛西",
area2 = "府中",
area2 = "調布",

area1 = "埼玉県"

area2 = "さいたま市"
area2 = "上尾市"
area2 = "桶川市"
area2 = "大宮"
area2 = "浦和"
area2 = "越谷市"
area2 = "熊谷市"


area1 = "大阪府"

area2 = "梅田"
area2 = "難波"
area2 = "心斎橋"
area2 = "天王寺"
area2 = "本町"
area2 = "鶴橋"
area2 = ""
area2 = ""
area2 = ""
area2 = ""
area2 = ""
area2 = ""
area2 = ""


area1 = "神奈川県"

area2 = "横浜市"
area2 = "鎌倉市"
area2 = "川崎市"
area2 = "小田原市"
area2 = "藤沢市"
area2 = "茅ヶ崎市"
area2 = "平塚市"
area2 = "厚木市"
area2 = "海老名市"
area2 = "横須賀市"
area2 = ""
area2 = ""
area2 = ""


# 食べログーーーーーーーーー
driver.get('https://tabelog.com/')
# origin_name = "Piacere"
scrape_one_sub.scrape_one(driver, "tb", area1, area2, "モスバーガー与野西口店")


def hover(elem):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(elem).perform()  # ホバー
hover(driver.find_element_by_id('js-leftnavi-area-anchor'))
driver.find_element_by_xpath('//span[text()="500m"]').click()

handle_array = driver.window_handles
driver.switch_to.window(handle_array[-1])


importlib.reload(scrape_one_sub)


# 半自動googleサーチーーーーーーーーー
# コード行の順番変えないように！
filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/調査部屋/doubt*.txt")
file = filepaths[0]
area1,area2 = file.split('_')[2],file.split('_')[3]
print(f"{area1} {area2}")
with open(file) as f:
    data = f.read()
name_list: list = data.strip().replace("生還    : ", "").split('\n\n')
name_iter = (name for name in name_list)
length = len(name_list)
driver.get('https://google.com/?hl=ja')
area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
area_input.send_keys(f'{area1} {area2} 飲食店' + Keys.ENTER)
driver.find_element_by_link_text('すべて表示').click()



def search_name(length:int):
    for name in name_iter:
        length -= 1
        print(f'あと{length}')
        # name = next(name_iter)
        print(name)
        store_mds = models.Media_data.objects.filter(store__store_name=name, store__area__area_name=f"{area1} {area2}")
        if not store_mds.exists():
            print('削除してあります\n')
            continue
        mt_list = [md.media_type.media_type for md in store_mds]
        if "google" in mt_list:
            print("googleあります\n")
            continue

        pyperclip.copy(name)

        address = store_mds[0].store.address
        category = [store_mds[0].store.category1, store_mds[0].store.category2, store_mds[0].store.category3]
        address2 = address.replace(area1, "")
        print(category)
        print(f'{address}')
        print(" / ".join(mt_list))
        revs = models.Review.objects.filter(media__in=store_mds)
        if revs.exists():
            latest_rev = revs.latest('review_date').review_date
            print(f'最新投稿： {latest_rev}')

        search_window = driver.find_element_by_xpath("//input[@aria-label='検索']")
        search_window.clear()
        sleep(0.5)
        # search_window.send_keys(f"{area_name} asobi")
        search_window.send_keys(f"{area1} {area2} {name}")
        search_window.submit()

        search_window = driver.find_element_by_xpath("//input[@aria-label='検索']")
        search_window.send_keys(f" ■{address2}")
        actions = webdriver.ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()  # 閉じる

        return name, length


def deleteAndAddClosedname(name):
    models.Store.objects.get(store_name=name, area__area_name=f"{area1} {area2}").delete()
    # 既存のファイルの末尾が改行になってるか
    try:
        with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "r") as f:
            lines = f.readlines()
        reads = lines[-1][-1]
        formated_lines = [line.strip() for line in lines]
    except Exception:
        reads = "\n"
        formated_lines = []
    with open(f"/Users/yutakakudo/Google ドライブ/colab/memo/closed/CLOSEDNAME_{area1}_{area2}.txt", "a") as f:
        if name not in formated_lines:
            if reads == "\n":
                f.write(name)
            else:
                f.write("\n")
                f.write(name)
            print('closed_list作成')
        else:
            print('すでにありました。')


name, length = search_name(length)
scrape_one_sub.scrape_one(driver, "google", area1, area2, name)
# scrape_one_sub.scrape_one(driver, "google", area1, area2, "やまちゃん")
deleteAndAddClosedname(name)

send2trash(file)

