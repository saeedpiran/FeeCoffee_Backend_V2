from rest_framework import serializers

from product_module.models import ProductBrand, ShopProductCategory, CafeProductCategory, Product, \
    ProductFeature, Feature, ProductBundleItem, ProductBundle, ProductMediaFiles
from shop_module.models import Shop


# ----------------------------------------------------------------------------
# Product Brands
class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ['id', 'title', 'en_title', 'slug', 'is_active']

    def validate_title(self, value):
        # Check if a brand with the same title already exists
        if ProductBrand.objects.filter(title=value).exists():
            raise serializers.ValidationError("برند با نام مشابه قبلاً ثبت شده است.")
        return value


# ----------------------------------------------------------------------------
# Shop products sub categories
class ShopProductsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProductCategory
        fields = [
            'id','title', 'url_title', 'slug', 'ordering_number', 'image', 'parent_category',
            'is_active'
        ]


# ----------------------------------------------------------------------------
# Cafe products sub categories
class WritableNestedFieldCategory(serializers.PrimaryKeyRelatedField):
    """
    Acts like a primary key field for write operations, but on read returns a full
    nested representation using the provided serializer_class.
    If the instance is incomplete (e.g. missing expected attributes), it refetches it.
    """

    def __init__(self, **kwargs):
        self.serializer_class = kwargs.pop("serializer_class")
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the instance does not have the expected attribute,
        # refetch it fully from the queryset.
        if not hasattr(value, "media_type"):
            value = self.get_queryset().get(pk=value.pk)
        return self.serializer_class(value, context=self.context).data


class ProductCategoryMediaFilesSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductMediaFiles
        fields = [
            'id',
            'file_url',
            'media_type',
            'caption',
            'is_active'
        ]

    def get_file_url(self, obj):
        request = self.context.get("request", None)
        if obj.file:
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class CafeProductsCategorySerializer(serializers.ModelSerializer):
    image = WritableNestedFieldCategory(
        serializer_class=ProductCategoryMediaFilesSerializer,
        queryset=ProductMediaFiles.objects.filter(
            media_type=ProductMediaFiles.CAFEPRODUCTCATEGORY
        ),
        required=False,
        allow_null=True
    )

    # Override the parent_category to return Persian values
    parent_category = serializers.SerializerMethodField()

    # Field to hold the count of products associated with each category.
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CafeProductCategory
        fields = [
            'id',
            'title',
            'url_title',
            'slug',
            'ordering_number',
            'shop',
            'image',  # On GET, returns nested info; on write, expect a file ID.
            'parent_category',
            'is_active',
            'is_deleted',
            'is_verified',
            'products_count',
            'created_date',
            'updated_date'
        ]
        read_only_fields = ('shop','created_date','updated_date')  # Make shop read-only on input.
        extra_kwargs = {
            'is_verified': {'required': False},
            'url_title': {'required': False},
            'created_date': {'required': False},
            'updated_date': {'required': False},
        }

    def get_parent_category(self, obj):
        # Fetch Persian name from the choices
        category_dict = dict(CafeProductCategory.CAFE_MENU_CATEGORY_TYPE_CHOICES)
        return category_dict.get(obj.parent_category, obj.parent_category)  # Fallback to original if not found

class EmptyRestoreSerializer(serializers.Serializer):
    pass


# ----------------------------------------------------------------------------
# Product
# A field to treat image relationships: writing via IDs and reading nested data.
class WritableNestedFieldProduct(serializers.PrimaryKeyRelatedField):
    """
    Acts like a primary key field for write operations,
    but on read returns a nested representation using the provided serializer_class.
    If the object is incomplete (i.e. missing an expected attribute),
    it refetches the instance from the database.
    """

    def __init__(self, **kwargs):
        self.serializer_class = kwargs.pop("serializer_class")
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the instance appears incomplete, refetch it.
        if not hasattr(value, "media_type"):
            value = self.get_queryset().get(pk=value.pk)
        return self.serializer_class(value, context=self.context).data


# ----------------------------------------------------------------
# Serializer for product-related images.
class ProductImageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductMediaFiles  # Ensure this is your correct media file model.
        fields = ['id', 'is_active', 'media_type', 'file_url', 'caption']

    def get_file_url(self, obj):
        request = self.context.get("request", None)
        if obj.file:
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


# ----------------------------------------------------------------
# This serializer describes the constant Feature attributes as defined by admin.
class NestedFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'title', 'url_title', 'feature_type', 'slug', 'description']


# ----------------------------------------------------------------
# Write serializer for product feature associations.
class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['id', 'feature', 'feature_value', 'price' , 'final_price']


# ----------------------------------------------------------------
# Read serializer for product feature associations that nests the constant feature data.
class ProductFeatureNestedSerializer(serializers.ModelSerializer):
    feature = NestedFeatureSerializer(read_only=True)

    class Meta:
        model = ProductFeature
        fields = ['id', 'feature', 'feature_value', 'price', 'final_price']

# -------------------------------------------------------------------------
# First, create a nested serializer for your Brand model.
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand  # replace with your actual Brand model
        fields = ['id', 'title']  # list the fields you want in the nested representation

# -------------------------------------------------------------------------
# Now, define a custom field that will behave like a PrimaryKeyRelatedField on input,
# but will output a nested representation using BrandSerializer on GET.
class BrandNestedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        # If the instance does not have the required attribute (e.g. 'title'),
        # then re-fetch the complete Brand instance from the database.
        if not hasattr(value, 'title'):
            # from your_app.models import Brand  # Adjust the import as necessary
            value = ProductBrand.objects.get(pk=value.pk)
        return BrandSerializer(value, context=self.context).data



# ----------------------------------------------------------------
# # Optional: The Feature serializer for admin views.
# class FeatureSerializer(serializers.ModelSerializer):
#     feature_values = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Feature
#         fields = ['id', 'title', 'url_title', 'feature_type', 'slug', 'description', 'feature_values']
#
#     def get_feature_values(self, obj):
#         product_features = ProductFeature.objects.filter(feature=obj)
#         return ProductFeatureNestedSerializer(product_features, many=True, context=self.context).data


# ----------------------------------------------------------------
# Product serializer integrating both read (product_features) and write (features_data) representations.
class ProductSerializer(serializers.ModelSerializer):
    images = WritableNestedFieldProduct(
        source='image',  # maps serializer field 'images' to model field 'image'
        many=True,
        serializer_class=ProductImageSerializer,
        queryset=ProductMediaFiles.objects.filter(media_type=ProductMediaFiles.PRODUCT),
        required=False
    )
    # Read-only field: group product features by their parent feature.
    product_features = serializers.SerializerMethodField()
    # Write-only field to accept product feature entries.
    features_data = ProductFeatureSerializer(many=True, write_only=True, required=False)
    shop = serializers.PrimaryKeyRelatedField(read_only=True)

    # Use the custom brand field.
    # On input (create and update), it accepts an id.
    # On output (GET) it returns a nested object via BrandSerializer.
    brand = BrandNestedPrimaryKeyRelatedField(queryset=ProductBrand.objects.all(),
                                              required=False,
                                              allow_null=True
                                              )
    # New read-only field that sends a category name to the frontend.
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'ordering_number', 'en_name', 'slug', 'product_type', 'cafe_category',
            'category_name','shop_category', 'brand', 'price', 'discount', 'final_price',
            'short_description','description', 'created_date', 'updated_date', 'is_special', 'is_active',
            'is_wholesale', 'images', 'product_features', 'features_data', 'category', 'shop'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date', 'shop']
        extra_kwargs = {
            'short_description': {'required': False, 'allow_blank': True, 'allow_null': True},
            'description': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_product_features(self, obj):
        """Group all associated ProductFeature records by the admin-defined Feature."""
        grouped = {}
        # Iterate over each product-specific feature instance.
        for pf in obj.product_features.all():
            f = pf.feature  # the admin-defined feature
            if f.id not in grouped:
                grouped[f.id] = {
                    "id": f.id,
                    "title": f.title,
                    "url_title": f.url_title,
                    "feature_type": f.feature_type,
                    "slug": f.slug,
                    "description": f.description,
                    "feature_values": []
                }
            grouped[f.id]["feature_values"].append({
                "id": pf.id,
                "feature_value": pf.feature_value,
                "price": pf.price,
                "final_price": pf.final_price
            })
        return list(grouped.values())

    def get_category_name(self, obj):
        """
        Return the category title based on the product's type.
        - For a SHOP product, return the title of shop_category if available, otherwise "-".
        - For a CAFE product, return the title of cafe_category if available, otherwise "-".
        """
        if obj.product_type == Product.SHOP:
            return obj.shop_category.title if obj.shop_category else "-"
        elif obj.product_type == Product.CAFE:
            return obj.cafe_category.title if obj.cafe_category else "-"
        return "-"

    def create(self, validated_data):
        images = validated_data.pop('image', [])
        features_data = validated_data.pop('features_data', [])
        product = Product.objects.create(**validated_data)

        if images:
            product.image.set(images)

        for feature_data in features_data:
            feature_val = feature_data.get('feature')
            if not isinstance(feature_val, Feature):
                try:
                    feature_instance = Feature.objects.get(pk=feature_val)
                except Feature.DoesNotExist:
                    raise serializers.ValidationError({
                        "feature": f"Feature with id {feature_val} does not exist."
                    })
            else:
                feature_instance = feature_val

            ProductFeature.objects.create(
                product=product,
                feature=feature_instance,
                feature_value=feature_data.get('feature_value'),
                price=feature_data.get('price', 0)
            )
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('image', None)
        features_data = validated_data.pop('features_data', None)
        instance = super().update(instance, validated_data)

        if images is not None:
            instance.image.set(images)

        if images is not None:
            instance.image.set(images)

            # Check if features_data is provided
        if features_data is not None:
            # If it's an empty list, delete all associated product features.
            if not features_data:
                instance.product_features.all().delete()
            else:
                # You might want to update, add, or remove only specific features.
                # For simplicity, one approach is to clear all features first, and then add the provided ones.
                # Alternatively, implement logic to diff the current features vs. provided data.

                # Option 1: Clear all and recreate
                instance.product_features.all().delete()
                for feature_data in features_data:
                    feature_val = feature_data.get('feature')
                    if not isinstance(feature_val, Feature):
                        try:
                            feature_instance = Feature.objects.get(pk=feature_val)
                        except Feature.DoesNotExist:
                            raise serializers.ValidationError({
                                "feature": f"Feature with id {feature_val} does not exist."
                            })
                    else:
                        feature_instance = feature_val
                    ProductFeature.objects.create(
                        product=instance,
                        feature=feature_instance,
                        feature_value=feature_data.get('feature_value'),
                        price=feature_data.get('price', 0)
                    )
                # Option 2: More refined update logic (update existing, add new, delete missing)
                # would require you to compare the IDs of the current features with the IDs
                # provided in 'features_data' and then do the respective operations.
        return instance

        # # Here we're updating product features without removing existing ones entirely.
        # if features_data is not None:
        #     for feature_data in features_data:
        #         pf_id = feature_data.get("id", None)
        #         feature_val = feature_data.get('feature')
        #         if not isinstance(feature_val, Feature):
        #             try:
        #                 feature_instance = Feature.objects.get(pk=feature_val)
        #             except Feature.DoesNotExist:
        #                 raise serializers.ValidationError({
        #                     "feature": f"Feature with id {feature_val} does not exist."
        #                 })
        #         else:
        #             feature_instance = feature_val
        #
        #         if pf_id:
        #             # Update an existing ProductFeature record.
        #             try:
        #                 pf_obj = ProductFeature.objects.get(pk=pf_id, product=instance)
        #             except ProductFeature.DoesNotExist:
        #                 raise serializers.ValidationError({
        #                     "id": f"ProductFeature with id {pf_id} not found for this product."
        #                 })
        #             pf_obj.feature_value = feature_data.get("feature_value", pf_obj.feature_value)
        #             pf_obj.price = feature_data.get("price", pf_obj.price)
        #             pf_obj.save()
        #         else:
        #             # Create a new ProductFeature record.
        #             ProductFeature.objects.create(
        #                 product=instance,
        #                 feature=feature_instance,
        #                 feature_value=feature_data.get('feature_value'),
        #                 price=feature_data.get('price', 0)
        #             )
        # return instance





# # Feature with related product feature values
# class FeatureSerializer(serializers.ModelSerializer):
#     feature_values = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Feature
#         fields = ['id', 'title', 'url_title', 'feature_type', 'slug', 'description', 'feature_values']
#
#     def get_feature_values(self, obj):
#         # Group feature values related to the current feature.
#         feature_values = ProductFeature.objects.filter(feature=obj)
#         return ProductFeatureSerializer(feature_values, many=True).data


# class ProductSerializer(serializers.ModelSerializer):
#     images = WritableNestedFieldProduct(
#         source='image',  # map serializer field 'images' to model field 'image'
#         many=True,
#         serializer_class=ProductImageSerializer,
#         queryset=ProductMediaFiles.objects.filter(media_type=ProductMediaFiles.PRODUCT),
#         required=False
#     )
#     features = serializers.SerializerMethodField()  # computed field for GET requests
#     features_data = ProductFeatureSerializer(many=True, write_only=True, required=False)
#     shop = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'en_name', 'slug', 'product_type', 'cafe_category',
#             'shop_category', 'brand', 'price', 'discount', 'short_description',
#             'description', 'created_date', 'updated_date', 'is_special', 'is_active',
#             'show_in_shop', 'is_deleted', 'is_verified', 'is_wholesale', 'images', 'features',
#             'features_data', 'category', 'shop'
#         ]
#         read_only_fields = ['id', 'created_date', 'updated_date', 'shop']
#
#     def get_features(self, obj):
#         grouped = {}
#         for pf in obj.product_features.all():
#             feat = pf.feature
#             if feat.id not in grouped:
#                 grouped[feat.id] = {
#                     'id': feat.id,
#                     'title': feat.title,
#                     'url_title': feat.url_title,
#                     'slug': feat.slug,
#                     'description': feat.description,
#                     'feature_values': []
#                 }
#             grouped[feat.id]['feature_values'].append({
#                 'id': pf.id,
#                 'feature_value': pf.feature_value,
#                 'price': pf.price
#             })
#         return list(grouped.values())
#
#     def create(self, validated_data):
#         images = validated_data.pop('image', [])
#         features_data = validated_data.pop('features_data', [])
#         product = Product.objects.create(**validated_data)
#
#         if images:
#             product.image.set(images)
#
#         for feature_data in features_data:
#             feature_id = feature_data.get('feature')
#             try:
#                 feature_instance = Feature.objects.get(pk=feature_id)
#             except Feature.DoesNotExist:
#                 raise serializers.ValidationError({
#                     "feature": f"Feature with id {feature_id} does not exist."
#                 })
#             ProductFeature.objects.create(
#                 product=product,
#                 feature=feature_instance,
#                 feature_value=feature_data.get('feature_value'),
#                 price=feature_data.get('price', 0)
#             )
#         return product
#
#     def update(self, instance, validated_data):
#         images = validated_data.pop('image', None)
#         features_data = validated_data.pop('features_data', [])
#         instance = super().update(instance, validated_data)
#
#         if images is not None:
#             instance.image.set(images)
#
#         for feature_data in features_data:
#             feature_id = feature_data.get('feature')
#             try:
#                 feature_instance = Feature.objects.get(pk=feature_id)
#             except Feature.DoesNotExist:
#                 raise serializers.ValidationError({
#                     "feature": f"Feature with id {feature_id} does not exist."
#                 })
#             ProductFeature.objects.create(
#                 product=instance,
#                 feature=feature_instance,
#                 feature_value=feature_data.get('feature_value'),
#                 price=feature_data.get('price', 0)
#             )
#         return instance


# ------------------------------------------------------------------------------
# Bundle
class ProductBundleItemWriteSerializer(serializers.ModelSerializer):
    # Accepts a product primary key and quantity for write operations.
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = ProductBundleItem
        fields = ['product', 'quantity']


class ProductBundleItemReadSerializer(serializers.ModelSerializer):
    # Returns a simplified representation of the product.
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductBundleItem
        fields = ['id', 'product', 'quantity']

    def get_product(self, obj):
        # Safely retrieve the first image URL from the product.
        first_image_url = None
        if hasattr(obj.product, 'get_first_image_url'):
            try:
                first_image_url = obj.product.get_first_image_url()
            except Exception:
                first_image_url = None

        return {
            'id': str(obj.product.id),
            'name': obj.product.name,
            'first_image_url': first_image_url,
        }


class ProductBundleSerializer(serializers.ModelSerializer):
    # The shop is provided as a primary key.
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    # For read purposes, include the bundle items using a nested read serializer.
    bundle_items = ProductBundleItemReadSerializer(many=True, read_only=True)
    # For write purposes, accept bundle item data.
    bundle_items_data = ProductBundleItemWriteSerializer(many=True, write_only=True)
    # Retrieve bundle image from its products.
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductBundle
        fields = [
            'id',
            'shop',
            'title',
            'bundle_price',
            'is_active',
            'is_verified',
            'bundle_items',
            'bundle_items_data',
            'image_url'
        ]

    def get_image_url(self, obj):
        # Return the image URL generated by the ProductBundle's method.
        return obj.get_image_url()

    def create(self, validated_data):
        # Pop out bundle items data
        items_data = validated_data.pop('bundle_items_data', [])
        bundle = ProductBundle.objects.create(**validated_data)
        for item_data in items_data:
            ProductBundleItem.objects.create(bundle=bundle, **item_data)
        return bundle

    def update(self, instance, validated_data):
        items_data = validated_data.pop('bundle_items_data', [])
        # Update bundle fields first.
        instance = super().update(instance, validated_data)
        # Remove current items and re-create them.
        instance.bundle_items.all().delete()
        for item_data in items_data:
            ProductBundleItem.objects.create(bundle=instance, **item_data)
        return instance

# ----------------------------------------------------------------
# Features
# Optional: The Feature serializer for admin views.
class FeatureSerializer(serializers.ModelSerializer):
    # feature_values = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = ['id', 'title', 'url_title', 'feature_type', 'slug', 'description']

    # def get_feature_values(self, obj):
    #     product_features = ProductFeature.objects.filter(feature=obj)
    #     return ProductFeatureNestedSerializer(product_features, many=True, context=self.context).data

# ------------------------------------------------------------------------------
# Active and Inactive the Product
class ProductToggleActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'is_active']

# -----------------------------------------------------------------
# Price, Discount and ordering number change
class ProductPricingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['price', 'discount', 'ordering_number']

# -----------------------------------------------------------------
# File manager
class ProductMediaFilesSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True)
    # is_global = serializers.BooleanField(required=False)  # Allow client input but override in perform_create.
    is_active = serializers.BooleanField(default=True)  # Add default=True here

    class Meta:
        model = ProductMediaFiles
        fields = [
            'id',
            'media_type',
            'media_category',
            'file',
            'file_url',
            'caption',
            'is_active',  # Still visible but handled by the model's default.
        ]
        read_only_fields = ['id', 'created_date']  # Mark is_active as read-only.



    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

# -----------------------------------------------------------