from django.core.management.base import BaseCommand
from scrape.insert.insert_from_json_gn import insert_from_json_gn
import json


class Command(BaseCommand):  # コマンド python manage.py ~~
    def handle(self, *args, **options):

        file = "/Users/yutakakudo/Downloads/gn_2021-06-10_1839.json"

        # 決めておくーーーーーーー
        area1 = "千葉県"
        area2 = "船橋市"
        media_type = "gn"
        # 決めておくーーーーーーー

        insert_from_json_gn(file, area1, area2, media_type)

        # return super().handle(*args, **options)
