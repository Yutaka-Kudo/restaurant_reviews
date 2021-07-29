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
        # filepaths = glob("/Users/yutakakudo/Google ドライブ/colab/json/tb_埼玉県_浦和_1から28_2021-07-27_0314.json")
        for file in filepaths:
            filename = os.path.basename(file)
            # subprocess.run(['say', 'スタート'])
            subprocess.run(['noti', '-m', f"start! {filename}"])

            area1 = file.split('_')[1]
            area2 = file.split('_')[2]
            print(f"{area1} {area2}")

            media_type = file.split('_')[0].split('/')[-1]
            print(f"media_type {media_type}")

            importlib.reload(scrape.insert.insert_from_json)
            print("モジュールリロード")

            scrape.insert.insert_from_json.insert_from_json(file, area1, area2, media_type)

            try:
                shutil.move(file, "/Users/yutakakudo/Google ドライブ/colab/json/使用済2")
            except Exception as e:
                os.remove(file)
                print(type(e), e)
                print('ファイルが重複していましたが、削除して続けます。')

        subprocess.run(['noti', '-m', "!!!!!!!End!!!!!!!"])

        # if media_type == "gn":
        #     insert_from_json_gn(file, area1, area2, media_type)
        # elif media_type == "tb":
        #     insert_from_json_tb(file, area1, area2, media_type)
        # elif media_type == "google":
        #     insert_from_json_google(file, area1, area2, media_type)
        # elif media_type == "hp":
        # insert_from_json_hp(file, area1, area2, media_type)

        # return super().handle(*args, **options)
