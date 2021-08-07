import re
import json
from dateutil.relativedelta import relativedelta
from pprint import pprint as pp
from devtools import debug
import pytz
import datetime
from bs4 import BeautifulSoup
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


def scrape_google():

    from selenium import webdriver
    import random
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

    options.add_argument('--window-size=1200,1000')

    # from webdriver_manager.chrome import ChromeDriverManager
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

    # from scrape import driver_settings

    try:
        from my_module import capture, Wait_located
        from scrape_kit import generate_json, endpage_memo, address_ng_memo
    except ImportError:
        from site_packages.my_module import capture, Wait_located
        from scrape.scrape_kit import generate_json, endpage_memo, address_ng_memo

    area1 = "千葉県"
    area2s = [
        # {"船橋市": 18},
        # {"市川市": 17},
        {"千葉市": 12},
        # {"松戸市": 14},
        # {"銚子市": },

        # {"館山市": 12},
        # {"柏市": },
        # {"木更津市": },
        # {"習志野市": 13},
    ]

    # area1 = "東京都"
    # area2s = [
    #     # {"中目黒": 15},
    #     # {"新宿": },
    #     # {"渋谷": },
    #     # {"吉祥寺": },
    #     # {"銀座": },
    #     # {"新橋": },
    #     # {"六本木": },
    #     # {"大久保": },
    #     # {"池袋": },
    #     # {"有楽町": },
    #     # {"日本橋": },
    #     # {"お台場": },
    #     # {"中野": },
    #     # {"北千住": },
    #     # {"町田": },
    #     # {"高田馬場": },
    #     # {"上野": },
    #     # {"浅草": },
    #     # {"恵比寿": },
    #     # {"練馬": },
    #     # {"板橋": },
    #     # {"赤羽": },
    #     # {"国分寺": },
    #     # {"麻布": },

    #     # {"原宿": },
    #     # {"青山": },
    #     # {"秋葉原": },
    #     # {"水道橋": 12},
    #     # {"自由が丘": 14},
    #     # {"三軒茶屋": 13},
    #     # {"二子玉川": },
    #     # {"錦糸町": },
    #     # {"押上": },
    #     # {"新小岩": },
    #     # {"蒲田": },
    #     # {"立川": },
    #     # {"八王子": },
    #     # {"新小岩": },
    #     # {"神楽坂": },
    #     # {"巣鴨": },
    #     # {"品川": },
    #     # {"五反田": },
    #     # {"大崎": },
    #     # {"下北沢": },
    #     # {"明大前": },
    #     # {"人形町": },
    #     # {"門前仲町": },
    #     # {"葛西": },
    #     # {"府中": },
    #     # {"調布": },

    # ]

    # area1 = "埼玉県"
    # area2s = [
    #     # {"さいたま市": },
    #     # {"桶川市": 10},
    #     {"上尾市": 15},
    # ]

    # area1 = "大阪府"
    # area2s = [
    #     # {"梅田": },
    #     # {"難波": },
    #     # {"心斎橋": },
    #     {"天王寺": },
    #     {"本町": },
    #     {"鶴橋": },
    #     # {"": },
    #     # {"": },
    #     # {"": },
    #     # {"": },
    #     # {"": },
    #     # {"": },
    # ]

    # area1 = "神奈川県"
    # area2s = [
    #     # {"横浜市": },
    #     # {"鎌倉市": },
    #     # {"川崎市": },
    #     {"小田原市": },
    #     {"藤沢市": },
    #     {"茅ヶ崎市": },
    #     {"平塚市": },
    #     {"厚木市": },
    #     {"海老名市": },
    #     {"横須賀市": },
    #     # {"": },
    #     # {"": },
    #     # {"": },
    # ]

    area_list = []
    for area2 in area2s:
        area_list.append([area1, area2])

    media = "google"

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
    HAN2ZEN = str.maketrans(HAN, ZEN)

    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_settings.options)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    for area1, area2dict in area_list:
        area2 = list(area2dict.keys())[0]
        range_last = list(area2dict.values())[0] + 1
        page_range = range(1, range_last)
        print("page_range", page_range)

        driver.get('https://google.com/?hl=ja')

        area_input = driver.find_element_by_css_selector('body > div > div:nth-child(3) > form > div > div > div > div > div:nth-child(2) > input')
        area_input.send_keys(f'{area1+area2} 飲食店' + Keys.ENTER)
        sleep(2)

        # google検索を引き続きご利用いただく前に、、、
        try:
            driver.find_element_by_xpath('//div[text()="同意する"]').click()
            sleep(2)
        except NoSuchElementException:
            pass

        driver.find_element_by_link_text('すべて表示').click()
        sleep(2)

        atode_list = []
        created_list = []
        already_list = []

        address_ng_list = []

        debug_list = []

        page_end_flg = False
        store_end_flg = False

        start_page = list(page_range)[0]
        for page_num in page_range:  # ページーーーーーーーーーーーーー

            if store_end_flg is True:
                break

            print('ぺーーーーーじーーーーーーーー')
            debug(page_num)

            # 大きいページ番号からスタートの際のページ送り
            # googleの場合、1ページごとにリロードしなくちゃならないので
            if page_num != 1:
                # 10以上なら目的のページ数まで送る
                if page_num >= 10:
                    this_page = 10
                    # this_page10固定だと10ページ目の際動かないのでpage_num11の際だけthis_pageいじる。page_num11 → 現在ページ10
                    if page_num == 11:
                        this_page = 9
                    try:
                        while page_num >= this_page:
                            driver.find_element_by_xpath(f"//a[@aria-label='Page {this_page}']").click()
                            # dw.wait_lacated_xpath(f"//a[@aria-label='Page {this_page}']").click()
                            print(f'ページ移動中...{this_page}')
                            sleep(5)  # これ強め必要
                            this_page += 1
                    except NoSuchElementException as e:
                        print(type(e), e)
                        page_end_flg = True
                        break
                    except Exception as e:
                        print(type(e), e)
                        print('ページ遷移エラー')
                        break
                        # raise Exception

                # 8未満ならそのままいける
                else:
                    try:
                        driver.find_element_by_xpath(f"//a[@aria-label='Page {page_num}']").click()
                    except Exception:
                        page_end_flg = True
                        break

            sleep(3)

            # 1ページ目の広告枠＋3個のあとにおすすめページに誘われるのでそこをスルー
            # store_list_wrap = driver.find_element_by_css_selector('div.rl_tile-group > div:nth-of-type(4)')
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

            for store_num in range(1, 21):  # 店ーーーーーーーーーーーーーーーー
                # for store_num in range(1, 3):  # 店ーーーーーーーーーーーーーーーー
                atode_dict = {}
                atode_flg = False
                # ng_flg = False
                sleep(1)
                if page_num == 1 and store_num == ad_count + 4:
                    print('skip!!!!')
                else:
                    try:
                        debug(store_num)
                        driver.find_element_by_css_selector(f'div.rl_full-list > div > div > div > div:nth-child(4) > div:nth-child({store_num})').click()
                        sleep(1)
                    except NoSuchElementException:
                        print('最後までいきました。')
                        page_end_flg = True
                        store_end_flg = True
                        break

                    try:
                        store_name = driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div > div > div > h2').text
                    except Exception:
                        store_name = ""
                        # ng_flg = True
                        continue

                    if store_name in IGNORE_NAME_LIST or re.match(".*駅$", store_name):  # 多分Googleだけ、変な名前や施設名
                        # ng_flg = True
                        continue

                    # あとで「〜〜駅」とかも除外できるようにーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

                    # かぶり店
                    if store_name in already_list:
                        print('かぶりスキップ！')
                        sleep(1)
                        continue

                    # if ng_flg == False:
                    atode_dict["name"] = store_name
                    # akp_tsuid137 > div > div:nth-child(1) > div > div > div > div.kp-blk.knowledge-panel.Wnoohf.OJXvsb > div > div.ifM9O > div > div.kp-header > div > div:nth-child(2) > div:nth-child(1) > div > div > span.hqzQac > span > a > span
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

                    # 口コミボタンクリック
                    no_review_flg = False
                    try:
                        driver.find_element_by_css_selector('div.xpdopen > div > div > div > div > div:nth-child(2) > div > div > div > span:nth-child(3) > span > a').click()
                        sleep(1.5)
                    except Exception:
                        try:
                            driver.find_element_by_xpath('//span[contains(text(),"他の Google レビュー")]').click()
                            sleep(1.5)
                        except Exception:
                            print('口コミクリックエラー')
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

                    # if not ng_flg:
                    if not no_review_flg:

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

                        # driver.find_element_by_xpath(f'/html/body/span[{store_num}]/g-lightbox/div[2]/div[2]').click() # 閉じるボタン
                        actions = webdriver.ActionChains(driver)
                        actions.send_keys(Keys.ESCAPE).perform()  # 閉じる

                    atode_dict["review"] = atode_review_list

                    atode_list.append(atode_dict)

                    already_list.append(store_name)

            driver.refresh()
            sleep(2)
            try:
                driver.find_element_by_xpath("//button[@aria-label='Google 検索']").click()  # リフレッシュ
            except Exception:
                # たまにストアリンクが19個しかなく20個目に変なページへ飛ばされるのでバックする
                driver.back()
                sleep(2)
                driver.find_element_by_xpath("//button[@aria-label='Google 検索']").click()  # リフレッシュ
            sleep(2)

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
