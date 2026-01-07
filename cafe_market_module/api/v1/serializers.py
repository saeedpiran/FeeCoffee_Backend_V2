from rest_framework import serializers

from cafe_market_module.models import CafeMarketBanner
from shop_module.models import Shop


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'is_special']
#
# class ProductBundleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductBundle
#         fields = ['id', 'title', 'is_active']
#


class CafeSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)
    has_special = serializers.SerializerMethodField()
    has_bundle = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    latitude = serializers.DecimalField(source='profile.latitude', max_digits=15, decimal_places=10, read_only=True)
    longitude = serializers.DecimalField(source='profile.longitude', max_digits=15, decimal_places=10, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'latitude', 'longitude', 'district', 'shop_type', 'is_verified', 'pickup',
                  'free_delivery',
                  'distance', 'has_special', 'has_bundle', 'banner_url']

    def get_has_special(self, obj):
        return obj.products.filter(is_special=True).exists()

    def get_has_bundle(self, obj):
        return obj.bundles.filter(is_active=True).exists()

    def get_banner_url(self, obj):
        request = self.context.get('request')
        banner_instance = obj.banner.first()  # Get the first banner instance from the ManyToManyField
        if banner_instance and banner_instance.file and request:
            return request.build_absolute_uri(banner_instance.file.url)
        return None

    def get_district(self, obj):
        # Ensure address is an empty string if None
        address = getattr(obj.profile, 'address', '') or ''
        address_parts = address.split('،') if address else []
        district = address_parts[0].strip() if address_parts else "محله ناشناخته"

        # Access city from ShopProfile and handle cases where it might be missing
        city = getattr(obj.profile, 'city', None)

        return f"{city}, {district}" if city else "موقعیت ناشناخته"


class CafeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeMarketBanner
        fields = ['id', 'title', 'image', 'created_date', 'is_active']

    # def get_abs_url(self, obj):
    #     request = self.context.get('request')
    #     return request.build_absolute_uri(obj.id)

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     if not request:
    #         raise ValidationError({
    #             "success": False,
    #             "error": "Request context is missing."
    #         })
    #
    #     user = request.user
    #     if not user.is_authenticated:
    #         raise ValidationError({
    #             "success": False,
    #             "error": "کاربر مجاز نیست."
    #         })
    #
    #     validated_data['author'] = user  # Assign the User instance directly
    #     return super().create(validated_data)
