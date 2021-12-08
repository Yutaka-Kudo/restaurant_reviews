# from scrape.insert.insert_from_json import insert_from_json
import scrape.insert.insert_from_json
from django.core.management.base import BaseCommand
# import json
import os
from glob import glob
import shutil
import subprocess
import importlib


class Command(BaseCommand):  # コマンド python manage.py ~~
    def handle(self, *args, **options):

        filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/*.json")
        # filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/tb_東京都_浅草_18から39_2021-08-04_0242.json")
        # filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/振り分けリスト/google_東京都_二子玉川駅_update_2021-08-24_1756.json")

        prefixes = list(set(["_".join(file.split('_')[:3]) for file in filepaths]))
        prefixes = sorted(prefixes, reverse=True)  # tbを先にできるか
        file_group = []
        for prefix in prefixes:
            file_group.append([file for file in filepaths if prefix in file])

        is_atode_file = ""
        for file_list in file_group:
            filename = "/".join([os.path.basename(file) for file in file_list])
            # subprocess.run(['say', 'スタート'])
            subprocess.run(['noti', '-m', f"start! {filename}"])

            area1 = file_list[0].split('_')[1]
            area2 = file_list[0].split('_')[2]
            print(f"{area1} {area2}")

            media_type = file_list[0].split('_')[0].split('/')[-1]
            print(f"media_type {media_type}")

            if file_list[0].split('_')[3] == "update":
                is_atode_file = "update"
            if file_list[0].split('_')[3] == "regist":
                is_atode_file = "regist"

            importlib.reload(scrape.insert.insert_from_json)
            print("モジュールリロード insert_from_json")

            try:
                scrape.insert.insert_from_json.insert_from_json(file_list, area1, area2, media_type, is_atode_file=is_atode_file)
            except Exception as e:
                subprocess.run(['noti', "-m", "エラー"])
                raise Exception(type(e), e)

            for file in file_list:
                shutil.move(file, "/Users/yutakakudo/Google ドライブ/colab/json/使用済2")

        subprocess.run(['noti', '-m', "!!!!!!!End!!!!!!!"])

        # return super().handle(*args, **options)
