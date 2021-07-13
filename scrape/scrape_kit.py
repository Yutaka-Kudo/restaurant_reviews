import datetime
import json
import os


def generate_json(atode_list, media, area1, area2, start_page, page_num):
    if os.getenv('HOME') == "/root":
        json_path = "/content/drive/MyDrive/colab/json"
        n = datetime.datetime.now() + datetime.timedelta(hours=9)
    elif os.getenv('HOME') == "/Users/yutakakudo":
        json_path = "/Users/yutakakudo/Google ドライブ/colab/json"
        n = datetime.datetime.now()
    else:
        raise Exception()

    def date_trans_json(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d')
    with open(f"{json_path}/{media}_{area1}_{area2}_{start_page}から{page_num}_{n.strftime('%Y-%m-%d_%H%M')}.json", "w") as f:
        json.dump(atode_list, f, indent=4, default=date_trans_json)
    print('json dump 作成！！！！！！')


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
