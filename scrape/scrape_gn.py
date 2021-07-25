import pykakasi
from pprint import pprint as pp
import pytz
import datetime
from bs4 import BeautifulSoup
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import random


def scrape_gn():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    user_agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
        # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        ''
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
    # "中目黒",
    # "新宿",
    # "渋谷",
    # "吉祥寺",
    # "銀座",
    # "新橋",
    # "六本木",
    # "大久保",
    # "池袋",
    # "有楽町",
    # "日本橋",
    # "お台場",
    # "中野",
    # "北千住",
    # "町田",
    # "高田馬場",
    # "上野",
    # "浅草",
    # "恵比寿",
    # "練馬",
    # "板橋",
    # "赤羽",
    # "国分寺",

    # "麻布",
    # "原宿",
    # "青山",
    # "秋葉原",
    # "水道橋",
    # "自由が丘",
    # "三軒茶屋",
    # "二子玉川",
    # "錦糸町",
    # "押上",
    # "新小岩",
    # "蒲田",
    # "立川",
    # "八王子",
    # "新小岩",
    # "神楽坂",
    # "巣鴨",
    # "品川",
    # "五反田",
    # "大崎",
    # "下北沢",
    # "明大前",
    # "人形町",
    # "門前仲町",
    # "葛西",
    # "府中",
    # "調布",

    # ]

    # area1 = "埼玉県"
    # area2 = "さいたま市"
    # area2 = "上尾市"

    # area1 = "大阪府"
    # area2s = [
    #     # "梅田",
    #     # "難波",
    #     "心斎橋",
    #     # "天王寺",
    #     # "本町",
    #     # "鶴橋",
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
    #     # "",
    #     # "",
    #     # "",
    #     # "",
    # ]

    area_list = []
    for area2 in area2s:
        area_list.append([area1, area2])

    page_range = range(1, 50)
    # page_range = range(10,20)

    # page_range = range(30,60)

    media = "gn"

    alias_dict = {
        "麻布": "麻布十番",
        "青山": "青山一丁目",
        "大宮": "大宮市",  # 都内や大阪以外の場所ならダミーで「市」をつけたり。
        "浦和": "浦和市",
        "千葉市": "千葉駅市",
        # "" : "",
        # "" : "",
        # "" : "",
    }

    # driver = webdriver.Chrome('chromedriver', options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    sleep(3)
    dw = Wait_located(driver)  # 自作のWebDriverWait簡潔版

    start_page = list(page_range)[0]

    for area1, area2 in area_list:

        driver.get('https://www.gnavi.co.jp/')

        area_input = driver.find_element_by_id('js-suggest-area')
        area_input.send_keys(area1)
        dw.wait_lacated_class_name('p-search__button').click()
        sleep(5)

        # area2の別名あれば変更ーーーーーー
        # ぐるなび内に存在する駅名に変換
        try:
            area2alias = alias_dict[area2]
        except KeyError:
            area2alias = area2
        print(f'area2alias {area2alias}')
        # ーーーーーーーーーーーーーーーー

        if area1 == "東京都" or area1 == "大阪府":
            input_area = driver.find_element_by_id('js-headbar-input-area')
            input_area.clear()
            input_area.send_keys(area2alias)

        else:
            try:
                driver.find_element_by_class_name('search-group__block-trigger').click()
                sleep(1)
                driver.find_elements_by_xpath(f"//a[contains(@data-value,'{area2alias[:-1]}')]")[-1].click()
                sleep(1)
                driver.find_element_by_xpath("//input[@value='検索する']").click()
                sleep(5)
                driver.find_element_by_class_name('search-group__block-trigger').click()
                sleep(1)
                driver.find_element_by_link_text('市区町村').click()
                sleep(1)
                driver.find_element_by_link_text(area2alias).click()
                sleep(1)
                print('エリア選択OK')
            except Exception:  # 選択肢がなければサーチボックスに直接area2を入力
                input_area = driver.find_element_by_id('js-headbar-input-area')
                input_area.clear()
                input_area.send_keys(area2alias[:-1])
                print('直接入力')

        dw.wait_lacated_xpath("//input[@value='検索する']").click()
        sleep(5)

        # 「全〜件」が表示されなければエラーにする
        try:
            print(driver.find_element_by_id('gn_pageH1').text)
            driver.find_element_by_class_name('result-stats')
        except Exception:
            print('エリア入力のエラー')
            driver.quit()
            raise Exception()

        # if area2 != "千葉市":  # 市が大きくていくつかに分かれてる場合、無視してそのまま収集
        #     dw.wait_lacated_class_name('search-group__block-trigger').click()
        #     sleep(2)
        #     if area1 == "東京都" or area1 == "大阪府":
        #         # driver.find_elements_by_xpath(f"//a[@data-value='{area2}']")[-1].click()
        #         driver.find_element_by_xpath('//*[@id="js-dropdown-area"]/ul/li[3]/div').find_elements_by_partial_link_text(area2)[-1].click()

        #         # dw.wait_lacated_link_text(area2).click()
        #         sleep(1)
        #     else:
            # dw.wait_lacated_xpath("//input[@value='検索する']").click()
            # sleep(5)

        atode_list = []
        created_list = []

        address_ng_list = []

        already_list = []

        page_end_flg = False

        page_range = list(page_range)
        # 大きいページ番号からスタートの際のページ送り
        try:
            if page_range[0] >= 5:
                page_num = 5
                while page_range[0] > page_num:
                    driver.find_element_by_class_name('pagination__inner').find_element_by_link_text(f'{page_num}').click()
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
                        driver.find_element_by_class_name('pagination__inner').find_element_by_link_text(f'{page_num}').click()
                        sleep(3)
                    except Exception:
                        page_end_flg = True
                        print('最後までいきました。')
                        break

                store_link_list = driver.find_elements_by_class_name('result-cassette__box-inner')
                # store_link_list = driver.find_elements_by_class_name('result-cassette__box-inner')[:2]
                for elem in store_link_list:
                    sleep(1)
                    atode_dict = {}

                    elem.click()

                    sleep(2)

                    handle_array = driver.window_handles
                    driver.switch_to.window(handle_array[-1])
                    sleep(0.5)
                    print('handle OK!')

                    # 店名ーーーーーーーーーーーー
                    try:
                        store_name = driver.find_element_by_class_name('shop-info__name').text.strip()
                        store_name = " ".join(store_name.split('\n'))  # ぐるなび用 店名が2行にわかれてる
                        print(store_name)
                        atode_dict["name"] = store_name

                    except (NoSuchElementException, Exception):
                        try:
                            store_name = driver.find_element_by_id('header-main-name').text.strip()
                            store_name = " ".join(store_name.split('\n'))  # ぐるなび用 店名が2行にわかれてる
                            print(store_name)
                            atode_dict["name"] = store_name
                        except Exception:
                            # print('かぶりスキップ！')
                            driver.execute_script("window.close();")
                            driver.switch_to.window(handle_array[0])
                            sleep(1)
                            continue

                    # 広告枠のかぶり店
                    if store_name in already_list:
                        print('かぶりスキップ！')
                        driver.execute_script("window.close();")
                        driver.switch_to.window(handle_array[0])
                        sleep(1)
                        continue

                    # 読み仮名ーーーーーーーーーーーー
                    try:
                        yomi_kana = driver.find_element_by_class_name('shop-info__ruby').text.strip().replace(' ', '')
                    except Exception:
                        try:
                            yomi_kana = driver.find_element_by_id('header-main-ruby').text.strip().replace(' ', '')
                        except Exception:
                            yomi_kana = None

                    if yomi_kana:
                        kakasi = pykakasi.kakasi()
                        yomigana = "".join([s["hira"] for s in kakasi.convert(yomi_kana)])
                        yomi_roma = "".join([s["hepburn"] for s in kakasi.convert(yomigana)])
                        atode_dict["yomigana"] = yomigana
                        atode_dict["yomi_roma"] = yomi_roma
                        print(f'よみ {atode_dict["yomigana"]}')
                        print(f'ローマ {atode_dict["yomi_roma"]}')

                    # 住所ーーーーーーーーーーーーーー
                    try:
                        region = driver.find_element_by_class_name('region').text
                        try:
                            locality = driver.find_element_by_class_name('locality').text
                        except NoSuchElementException:
                            locality = ""
                        print(address)
                        address = region + " " + locality
                    except Exception:
                        address_ng_list.append(store_name)
                        address = ""
                        print('住所取得NG')
                    atode_dict["address"] = address

                    # media_data用ーーー
                    collected_date = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
                    atode_dict["collected"] = collected_date

                    atode_dict["url"] = driver.current_url

                    # 口コミーーーーーーーーーー
                    try:  # 口コミボタンが無い店もある
                        driver.find_element_by_link_text('口コミ').click()
                        sleep(1)
                        res = driver.page_source
                        soup = BeautifulSoup(res, 'html.parser')

                        try:
                            rate = driver.find_element_by_class_name('trip-advisor-rating-img').get_attribute('alt')
                            rate = float(rate)
                        except Exception:
                            rate = 0
                            print('no rate')
                        atode_dict["rate"] = rate

                        # try:  # 口コミが無い店もある
                        review_count = len(soup.select('li.trip-advisor-review__list'))
                        if review_count == 0:
                            raise Exception
                    except Exception:
                        print('口コミがありません。')
                    else:
                        print('口コミ発見！！')

                        # 「もっと見る」を全て展開ーーーーーーーー
                        # sleep(2)
                        tsuzukiwoyomu_list = driver.find_elements_by_class_name('plus')[:5]  # 範囲制限
                        try:
                            for i in tsuzukiwoyomu_list:
                                i.click()
                                sleep(0.6)  # 早すぎるとバグる
                        except Exception:
                            pass

                        items = soup.select('li.trip-advisor-review__list')[:4]  # 範囲制限
                        atode_review_list = []
                        for i, item in enumerate(items):
                            no_data_flg = False
                            try:
                                title = item.select_one('.trip-advisor-review-title').text.strip()
                            except IndexError:
                                try:  # タイトルが無い投稿は本文の先頭24文字をとる。
                                    title = item.select_one('.trip-advisor-review-text').text.strip()[:24] + "…"
                                except IndexError:  # 本文もない場合はpass
                                    no_data_flg = True
                                    print('no data!!')
                            try:
                                review_point = item.select_one('.trip-advisor-review-rating').select_one('img').get('alt')
                                review_point = int(review_point)
                                print(f'get point {review_point}点')
                            except Exception:  # 評価値がついてない場合は0で入れるので、その後の表示等の処理を注意
                                review_point = 0
                                print("can't get point...")

                            if no_data_flg is False:
                                content = item.select_one('.trip-advisor-review-text')
                                # content = items[1].select_one('.trip-advisor-review-text')
                                # content = "".join([s.text for s in content]).strip()
                                # <br>タグを\nに置き換える
                                [s.replace_with('\n') for s in content.select('br')]
                                content = content.text
                                # print(content)

                                try:
                                    review_date = item.select_one('.trip-advisor-review-day--visit').text
                                    review_date = review_date[review_date.find('：')+1:review_date.find('）')]
                                    review_date = datetime.datetime.strptime(review_date, '%Y年%m月')
                                    # print(review_date)
                                except (ValueError, AttributeError):
                                    review_date = None

                                # {"name":a,"name":a,"phone":a,"url":a,"rate":a,
                                # "review":[{"content":a,"date":a,"log_num":a},{....},{.....}]}
                                atode_review_dict = {}
                                atode_review_dict["title"] = title
                                atode_review_dict["content"] = content
                                atode_review_dict["date"] = review_date
                                atode_review_dict["review_point"] = review_point
                                atode_review_list.append(atode_review_dict)

                        atode_dict["review"] = atode_review_list

                        atode_dict["rate"] = rate
                        atode_dict["review_count"] = review_count

                    atode_list.append(atode_dict)

                    # 広告枠のかぶり店
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
