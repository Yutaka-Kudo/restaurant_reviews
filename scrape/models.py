from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField


class Area_major(models.Model):
    area_name = models.CharField("県名",  max_length=10, default="area", unique=True)
    yomigana = models.CharField("よみ",  max_length=20, null=True, blank=True)
    yomi_roma = models.CharField("yomi",  max_length=20, null=True, blank=True)

    def __str__(self):
        return str(self.area_name)


class Area(models.Model):
    major_area = models.ForeignKey(Area_major, on_delete=models.CASCADE, verbose_name="県名")
    area_name = models.CharField("地名",  max_length=100, default="area", unique=True)
    yomigana = models.CharField("よみ",  max_length=100, null=True, blank=True)
    yomi_roma = models.CharField("yomi",  max_length=100, null=True, blank=True)
    registed = models.IntegerField("登録数", null=True, blank=True)

    def __str__(self):
        return str(self.area_name)


class Media_type(models.Model):
    media_type = models.CharField("媒体名", max_length=10, unique=True)
    official_name = models.CharField("正式名称", max_length=20, default='name')

    def __str__(self):
        return str(self.media_type)


class Store(models.Model):
    store_name = models.CharField("店名", max_length=100, default="name")
    yomigana = models.CharField("よみがな", max_length=100, null=True, blank=True)
    yomi_roma = models.CharField("yomigana", max_length=200, null=True, blank=True)
    store_name_gn = models.CharField("店名gn", max_length=100, null=True, blank=True)
    store_name_hp = models.CharField("店名hp", max_length=100, null=True, blank=True)
    store_name_tb = models.CharField("店名tb", max_length=100, null=True, blank=True)
    store_name_retty = models.CharField("店名retty", max_length=100, null=True, blank=True)
    store_name_demaekan = models.CharField("店名demaekan", max_length=100, null=True, blank=True)
    store_name_uber = models.CharField("店名uber", max_length=100, null=True, blank=True)
    store_name_google = models.CharField("店名google", max_length=100, null=True, blank=True)
    area = models.ForeignKey(Area, verbose_name="エリア", on_delete=models.PROTECT)
    phone_number = models.CharField("電話", max_length=20, null=True, blank=True)
    category1 = models.CharField(max_length=100, null=True, blank=True)
    category2 = models.CharField(max_length=100, null=True, blank=True)
    category3 = models.CharField(max_length=100, null=True, blank=True)
    total_rate = models.DecimalField("総合レート",max_digits=3, decimal_places=2, null=True, blank=True)
    total_review_count = models.IntegerField("総合評価数", null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    
    def update_name(self, store_name: str, media: str = ""):
        if media == "":
            self.store_name = store_name
        else:
            setattr(self, f'store_name_{media}', store_name)
        self.save()

    def __str__(self):
        return str(self.store_name)

    class Meta:
        # verbose_name = ""
        # verbose_name_plural = ""
        constraints = [models.UniqueConstraint(fields=['store_name', 'area'], name="unique_storearea")]


class Media_data(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    media_type = models.ForeignKey(Media_type, on_delete=models.CASCADE)
    collected = models.DateField(null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    rate = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.IntegerField("評価数", null=True, blank=True)

    def __str__(self):
        return str(self.store)+" "+str(self.media_type)

    class Meta:
        # verbose_name = ""
        # verbose_name_plural = ""
        constraints = [models.UniqueConstraint(fields=['store', 'media_type'], name="unique_storemedia")]


class Review(models.Model):
    media = models.ForeignKey(Media_data, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    log_num_byTabelog = models.IntegerField("ログ数_食べログ", null=True, blank=True)
    review_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # 評価値がついてない場合は0で入れるので、その後の表示等の処理を注意

    def __str__(self):
        return str(self.media)
