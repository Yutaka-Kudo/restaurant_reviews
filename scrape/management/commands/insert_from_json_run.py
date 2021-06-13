from django.core.management.base import BaseCommand
import json

from scrape.insert.insert_from_json import insert_from_json


class Command(BaseCommand):  # コマンド python manage.py ~~
    def handle(self, *args, **options):

        file = "/Users/yutakakudo/Downloads/"\
            "gn_千葉県_船橋市_2021-06-13_1852.json"

        area1 = file.split('_')[1]
        area2 = file.split('_')[2]
        print(f"{area1} {area2}")

        media_type = file.split('_')[0].split('/')[-1]
        print(f"media_type {media_type}")

        insert_from_json(file, area1, area2, media_type)
        # if media_type == "gn":
        #     insert_from_json_gn(file, area1, area2, media_type)
        # elif media_type == "tb":
        #     insert_from_json_tb(file, area1, area2, media_type)
        # elif media_type == "google":
        #     insert_from_json_google(file, area1, area2, media_type)
        # elif media_type == "hp":
            # insert_from_json_hp(file, area1, area2, media_type)

        # return super().handle(*args, **options)
