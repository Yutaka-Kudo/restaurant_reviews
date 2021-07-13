import django_filters
from rest_framework import viewsets, filters

from scrape.models import Area_major, Area, Media_type, Store, Media_data, Review
from scrape.serializer import Area_majorSerializer, AreaSerializer, Media_typeSerializer, StoreSerializer, Media_dataSerializer, ReviewSerializer
# , Media_type_customSerializer


class Area_majorViewSet(viewsets.ModelViewSet):
    queryset = Area_major.objects.all().order_by('yomigana')
    serializer_class = Area_majorSerializer
    filter_fields = ["id", "area_name", "yomigana", "yomi_roma"]


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all().order_by('yomigana')
    serializer_class = AreaSerializer
    # filter_fields = "__all__"
    # __all__にするとidがきかなくなる
    filter_fields = ["id", "area_name", "yomigana", "yomi_roma", "major_area"]

    # filter_backends = [filters.SearchFilter] # これをつけると普通のfilterが機能しない
    # search_fields = ["area_name"]


# class Area_customViewSet(viewsets.ModelViewSet):
#     queryset = Area.objects.all()
#     serializer_class = AreaSerializer
#     filter_backends = [filters.SearchFilter]
#     filter_fields = ['id', 'area_name']
#     search_fields = ["area_name"]

#     def get_serializer(self, *args, **kwargs):
#         if self.action == 'list':
#             if 'fields[]' in self.request.query_params:
#                 kwargs['fields'] = self.request.query_params.getlist('fields[]')

#         return super().get_serializer(*args, **kwargs)


class Media_typeViewSet(viewsets.ModelViewSet):
    queryset = Media_type.objects.all()
    serializer_class = Media_typeSerializer
    filter_fields = ['id', 'media_type']
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["media_type", "official_name"]


# class Media_type_customViewSet(viewsets.ModelViewSet):
#     queryset = Media_type.objects.all()
#     serializer_class = Media_type_customSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["media_type", "official_name"]

#     def get_serializer(self, *args, **kwargs):
#         if self.action == 'list':
#             if 'fields[]' in self.request.query_params:
#                 kwargs['fields'] = self.request.query_params.getlist('fields[]')

#         return super().get_serializer(*args, **kwargs)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all().order_by('store_name')
    serializer_class = StoreSerializer
    filter_fields = ['id', 'area', "store_name"]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["store_name", "store_name_gn", "store_name_hp", "store_name_tb", "store_name_retty", "store_name_demaekan", "store_name_uber", "store_name_google", "area__area_name"]  # 二重__はforeignKey等のリレーション


class StoreSearchViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all().order_by('store_name')
    serializer_class = StoreSerializer
    # filter_fields = ['id', 'area', "store_name"]
    filter_backends = [filters.SearchFilter]
    search_fields = ["store_name", "yomigana", "yomi_roma"]


class Media_dataViewSet(viewsets.ModelViewSet):
    queryset = Media_data.objects.all()
    serializer_class = Media_dataSerializer
    filter_fields = ['id', 'store', 'media_type']
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["store__store_name", "media_type__media_type"]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-review_date')
    serializer_class = ReviewSerializer
    filter_fields = ['id', 'media',"media__store"]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ["media"]


# from scrape.scrape_tb import scrape_tb
# from scrape.scrape_google import scrape_google, scrape_google_get_storenames
# from scrape.scrape_uber import scrape_uber
# from scrape.scrape_hp import scrape_hp
# from scrape.scrape_gn import scrape_gn
# from django.http import HttpResponse

# def scrape_run(request):
#     area1 = "千葉県"
#     area2 = "船橋市"
#     # area2 = "市川市"
#     # area2 = "千葉市"
#     # area2 = "習志野市"
#     # area2 = "柏市"

#     # area1 = "埼玉県"
#     # area2 = "さいたま市"

#     # area1 = "東京都"
#     # area2 = "中目黒"

#     scrape_tb(area1, area2, range(2, 10))
#     # scrape_hp(area1, area2, range(1, 4))
#     # scrape_gn(area1, area2, range(1, 2))
#     # scrape_google(area1, area2, range(1, 5))

#     # scrape_google_get_storenames(area1, area2, range(5,10))

#     # scrape_uber(area1, area2)

#     # return super().handle(*args, **options)
#     return HttpResponse('すくれぴ')
