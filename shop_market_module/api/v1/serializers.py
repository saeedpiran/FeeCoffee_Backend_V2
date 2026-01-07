from rest_framework import serializers

from product_module.models import Product
from shop_market_module.models import ShopMarketBanner


class ProductSerializer(serializers.ModelSerializer):
    category_url_title = serializers.ReadOnlyField(source='category.url_title')
    image_url = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'is_active', 'is_wholesale', 'product_type', 'category_url_title', 'created_date',
                  'price', 'discount', 'image_url']
        ref_name = 'ShopMarketModuleProductSerializer'

    def get_product_type(self, obj):
        try:
            return obj.category.category_type.title
        except AttributeError:
            return "Unknown Type"

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.get_first_image_url() and request:
            return request.build_absolute_uri(obj.get_first_image_url())
        return None


class ShopMarketBannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ShopMarketBanner
        fields = ['id', 'title', 'image_url', 'created_date', 'is_active']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ShopBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopMarketBanner
        fields = ['id', 'title', 'image', 'created_date', 'is_active']
