from rest_framework import serializers

from scrape.models import Area, Media_type, Store, Media_data, Review


# class DynamicFieldsModelSerializer(serializers.ModelSerializer):
#     """
#     A ModelSerializer that takes an additional `fields` argument that
#     controls which fields should be displayed.
#     """

#     def __init__(self, *args, **kwargs):
#         # Don't pass the 'fields' arg up to the superclass
#         fields = kwargs.pop('fields', None)

#         # Instantiate the superclass normally
#         super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

#         if fields is not None:
#             # Drop any fields that are not specified in the `fields` argument.
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class Media_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media_type
        fields = '__all__'

# class Media_type_customSerializer(DynamicFieldsModelSerializer):
#     class Meta:
#         model = Media_type
#         fields = ("id", "media_type", "official_name")


class StoreSerializer(serializers.ModelSerializer):
    area = AreaSerializer()

    class Meta:
        model = Store
        fields = '__all__'

class Media_dataSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    media_type = Media_typeSerializer()

    class Meta:
        model = Media_data
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    media = Media_dataSerializer()

    class Meta:
        model = Review
        fields ='__all__'