from scrape.serializer import AreaSerializer
from django.urls import path
from rest_framework import routers
from scrape.views import AreaViewSet, Media_typeViewSet, StoreViewSet, Media_dataViewSet, ReviewViewSet
# , Area_customViewSet, Media_type_customViewSet

from scrape import views

app_name = 'scrape'

urlpatterns = [
    path('scrape/', views.scrape_run, name="scrape_run"),
]


router = routers.DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'media_type', Media_typeViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'media_data', Media_dataViewSet)
router.register(r'reviews', ReviewViewSet)

# router_custom = routers.DefaultRouter()
# router_custom.register(r'area', Area_customViewSet)
# router_custom.register(r'media_type', Media_type_customViewSet)
