from django.urls import path
from display import views


app_name = 'display'

urlpatterns = [
    path('', views.index, name="index"),
    path('admin', views.admin, name="admin"),
    path('store_list', views.store_list, name="store_list"),
    path('show_details/<str:area_q>/<str:store_q>', views.show_details, name="show_details"),
]
