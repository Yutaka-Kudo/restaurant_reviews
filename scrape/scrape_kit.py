import datetime
import json
import os


def generate_json(atode_list, media: str, area1: str, area2: str, start_page: int = 0, page_num: int = 0, update_or_regist: str = ""):
    if os.getenv('HOME') == "/root":
        json_path = "/content/drive/MyDrive/colab/json"
        n = datetime.datetime.now() + datetime.timedelta(hours=9)
    elif os.getenv('HOME') == "/Users/yutakakudo":
        json_path = "/Users/yutakakudo/Google ドライブ/colab/json"
        n = datetime.datetime.now()
    else:
        raise Exception()

    if update_or_regist:
        json_path += "/振り分けリスト"

    def date_trans_json(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d')

    if start_page:
        with open(f"{json_path}/あとで/{media}_{area1}_{area2}_{start_page}から{page_num}_{n.strftime('%Y-%m-%d_%H%M')}.json", "w") as f:
            json.dump(atode_list, f, indent=4, default=date_trans_json)
        print('json dump 作成！！！！！！')
    elif update_or_regist:
        with open(f"{json_path}/{media}_{area1}_{area2}_{update_or_regist}_{n.strftime('%Y-%m-%d_%H%M')}.json", "w") as f:
            json.dump(atode_list, f, indent=4, default=date_trans_json)
        print(f'{update_or_regist} リスト 作成！！！！！！')
    else:
        with open(f"{json_path}/{media}_{area1}_{area2}_補充_{n.strftime('%Y-%m-%d_%H%M')}.json", "w") as f:
            json.dump(atode_list, f, indent=4, default=date_trans_json)
        print('補充file 作成！！！！！！')


def endpage_memo(media, area1, area2, page_num):
    if os.getenv('HOME') == "/root":
        memo_path = "/content/drive/MyDrive/colab/memo"
        n = datetime.datetime.now() + datetime.timedelta(hours=9)
    elif os.getenv('HOME') == "/Users/yutakakudo":
        memo_path = "/Users/yutakakudo/Google ドライブ/colab/memo"
        n = datetime.datetime.now()
    else:
        raise Exception()

    with open(f"{memo_path}/endpage_{media}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}", "w") as f:
        f.write(f'{page_num}')
    print('endpage_memo 作成！')


def address_ng_memo(address_ng_list, media, area1, area2):
    if os.getenv('HOME') == "/root":
        memo_path = "/content/drive/MyDrive/colab/memo"
        n = datetime.datetime.now() + datetime.timedelta(hours=9)
    elif os.getenv('HOME') == "/Users/yutakakudo":
        memo_path = "/Users/yutakakudo/Google ドライブ/colab/memo"
        n = datetime.datetime.now()
    else:
        raise Exception()
    with open(f"{memo_path}/addressNG_{media}_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}", "w") as f:
        for store in address_ng_list:
            f.write(f'{store}\n')


def duplicated_by_google_memo(duplicated_list, area1, area2):
    if os.getenv('HOME') == "/root":
        memo_path = "/content/drive/MyDrive/colab/json"
        n = datetime.datetime.now() + datetime.timedelta(hours=9)
    elif os.getenv('HOME') == "/Users/yutakakudo":
        memo_path = "/Users/yutakakudo/Google ドライブ/colab/json"
        n = datetime.datetime.now()
    else:
        raise Exception()
    with open(f"{memo_path}/dupliGoogle_{area1}_{area2}_{n.strftime('%Y-%m-%d_%H%M')}.txt", "w") as f:
        f.write("\n".join(duplicated_list))
    print('Duplication file 作成！')
