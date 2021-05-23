from django.contrib import admin
from scrape.models import *


class AreaAdmin(admin.ModelAdmin):
    list_display = ["area_name"]


admin.site.register(Area, AreaAdmin)


class Media_typeAdmin(admin.ModelAdmin):
    list_display = ["media_type"]


admin.site.register(Media_type, Media_typeAdmin)


class StoreAdmin(admin.ModelAdmin):
    list_display = ["store_name", "area", "phone_number"]


admin.site.register(Store, StoreAdmin)


class Media_dataAdmin(admin.ModelAdmin):
    list_display = ["id","store", "media_type", "rate", "review_count"]


admin.site.register(Media_data, Media_dataAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ["media","review_point", "title", "review_date","id"]


admin.site.register(Review, ReviewAdmin)
