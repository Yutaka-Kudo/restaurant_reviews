from django.core.management.base import BaseCommand
from scrape.scrape_tb import scrape_tb
from scrape.scrape_google import scrape_google
from scrape.scrape_google_refill import scrape_google_refill
from scrape.scrape_uber import scrape_uber
from scrape.scrape_hp import scrape_hp
from scrape.scrape_gn import scrape_gn


class Command(BaseCommand):  # コマンド python manage.py ~~
    def handle(self, *args, **options):
        media = input('Enter media! ex.tb gn google :')
        # start = int(input('Enter start num: '))
        # end = int(input('Enter end num: '))
        # area1 = input('Enter area1 県: ')
        # area2 = input('Enter area2 市: ')

        # area1 = "千葉県"
        # area2 = "船橋市"
        # area2 = "市川市"
        # area2 = "千葉市"
        # area2 = "習志野市"
        # area2 = "柏市"

        # area1 = "埼玉県"
        # area2 = "さいたま市"

        # area1 = "東京都"
        # area2 = "中目黒"

        if media == "tb":
            scrape_tb()
        elif media == "hp":
            scrape_hp(area1, area2, range(start, end))
        elif media == "gn":
            scrape_gn()
        elif media == "google":
            scrape_google()
        elif media == "google_r":
            scrape_google_refill()
        elif media == "uber":
            scrape_uber()

            # return super().handle(*args, **options)
