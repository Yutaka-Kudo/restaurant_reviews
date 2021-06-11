from django.core.management.base import BaseCommand
from scrape.insert.insert_from_json_gn import insert_from_json_gn
import json


class Command(BaseCommand):  # コマンド python manage.py ~~
    def handle(self, *args, **options):

        file = "/Users/yutakakudo/Downloads/"\
            "gn_千葉県船橋市2021-06-11_1942.json"
        # 決めておくーーーーーーー
        area1 = "千葉県"
        # area1 = file.split('_')[1]
        # area2 = fff.split('_')[2]
        area2 = "船橋市"
        # area2 = "市川市"
        media_type = "gn"
        # 決めておくーーーーーーー

        insert_from_json_gn(file, area1, area2, media_type)

        # return super().handle(*args, **options)
