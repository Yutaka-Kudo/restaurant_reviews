from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

from devtools import debug
from pprint import pprint as pp
from dateutil.relativedelta import relativedelta

from scrape import driver_settings

import random

from scrape import scrape_one_sub

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
# options.add_argument('--blink-settings=imagesEnabled=false')  # 画像なし
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





area1 = "千葉県"
area2s = [
    # "船橋市",
    # "市川市",
    # "千葉市",
    # "習志野市",
    # "松戸市",
    # "銚子市",
    "館山市",
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
area2 = area2s[0]

# 食べログーーーーーーーーー
driver.get('https://tabelog.com/')
# origin_name = "Piacere"
scrape_one_sub.scrape_one(driver,"tb", area1, area2, "レストランヤマグチ")


handle_array = driver.window_handles
driver.switch_to.window(handle_array[-1])

# googleーーーーーーーーーーー
driver.get('https://google.com/?hl=ja')
area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
area_input.send_keys(f'{area1+area2} 飲食店' + Keys.ENTER)
driver.find_element_by_link_text('すべて表示').click()
scrape_one_sub.scrape_one(driver,"google", area1, area2, "ドン")


import importlib
importlib.reload(scrape_one_sub)
