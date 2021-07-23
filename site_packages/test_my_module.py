import unittest
from devtools import debug
import datetime
from dateutil.relativedelta import relativedelta

from sub import chain_replace

# from scrape import models


# class Test_find_latest_review(unittest.TestCase):
#     name = "ARATA"
#     area_obj = models.Area.objects.get(area_name="大阪府 梅田")
#     def find_latest_review(self, name):
#         store_obj = models.Store.objects.get(store_name=name, area=area_obj)
#         reviews = models.Review.objects.filter(media__store=store_obj)
#         rescue_flg = False
#         for rev in reviews:
#             if rev.review_date > datetime.datetime.now().date() - relativedelta(months=18):
#                 rescue_flg = True
#                 break
#         # return store_obj, rescue_flg
#         print("rescue_flg",rescue_flg)
#         self.assertEqual(rescue_flg, False)
    

class TestChainReplace(unittest.TestCase):
    def test_chain_replace(self):
        saboten_s = "新宿さぼてん 中野マルイ店"
        saboten_l = "とんかつ新宿さぼてん 中野マルイ店"
        ringer_s = "リンガーハット ショップス市川店"
        ringer_l = "長崎ちゃんぽん リンガーハット ショップス市川店"
        ringer_s2 = "リンガ ーハット ショップス市川店"
        ringer_l2 = "長崎ちゃん ぽん リンガーハット ショップス市川店"
        miraizaka_l = "旨唐揚げと居酒メシ ミライザカ 北千住店"

        replaced_saboten_s = chain_replace(saboten_s)
        debug(replaced_saboten_s)
        replaced_saboten_l = chain_replace(saboten_l)
        debug(replaced_saboten_l)
        replaced_ringer_s = chain_replace(ringer_s)
        debug(replaced_ringer_s)
        replaced_ringer_l = chain_replace(ringer_l)
        debug(replaced_ringer_l)
        replaced_ringer_s2 = chain_replace(ringer_s2)
        debug(replaced_ringer_s2)
        replaced_ringer_l2 = chain_replace(ringer_l2)
        debug(replaced_ringer_l2)
        replaced_miraizaka_l = chain_replace(miraizaka_l)
        debug(replaced_miraizaka_l)

        self.assertEqual(replaced_saboten_s, saboten_l.replace(' ', ''))
        self.assertEqual(replaced_saboten_l, saboten_s.replace(' ', ''))
        self.assertEqual(replaced_ringer_s, ringer_l.replace(' ', ''))
        self.assertEqual(replaced_ringer_l, ringer_s.replace(' ', ''))
        self.assertEqual(replaced_ringer_s2, ringer_l2.replace(' ', ''))
        self.assertEqual(replaced_ringer_l2, ringer_s2.replace(' ', ''))
        self.assertEqual(replaced_miraizaka_l, "ミライザカ 北千住店".replace(' ', ''))


if __name__ == "__main__":
    unittest.main()
