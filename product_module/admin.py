from django.contrib import admin
from django.utils import timezone

from .models import (
    Product,
    ProductBrand,
    ProductMediaFiles,  # New model replacing the old ProductImage
    ShopProductCategory,
    CafeProductCategory,
    Feature,
    ProductFeature,
    ProductBundle,
    ProductBundleItem,
)


# Inline for Product Features remains the same.
class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1
    fields = ('feature', 'feature_value', 'price', 'final_price')
    verbose_name = "Product Feature"
    verbose_name_plural = "Product Features"


# Admin for Product Model
class ProductAdmin(admin.ModelAdmin):
    # Include ProductFeature inline; no inline for images.
    inlines = [ProductFeatureInline]
    exclude = ['created_date']
    list_filter = ['is_active', 'is_verified', 'shop', 'brand']
    list_display = ['name', 'shop', 'price', 'is_active', 'is_deleted', 'is_special', 'brand', 'category']
    list_editable = ['is_active', 'is_special']
    search_fields = ['name', 'en_name', 'brand__title', 'short_description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'en_name', 'slug', 'short_description', 'description')
        }),
        ('Categorization & Branding', {
            'fields': ('cafe_category', 'shop_category', 'brand', 'product_type', 'shop')
        }),
        ('Additional Details', {
            'fields': ('price', 'discount','ordering_number', 'final_price', 'is_active', 'is_special', 'is_wholesale', 'show_in_shop', 'is_verified')
        }),
        ('Media Files', {
            'fields': ('image',),  # Many-to-many field for media files (as a default selection)
        }),
    )

    def category(self, obj):
        # Return the title from the relevant category field.
        if obj.cafe_category:
            return obj.cafe_category.title
        elif obj.shop_category:
            return obj.shop_category.title
        return None

    category.short_description = "Category"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_date = timezone.now()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return Product.all_objects.all()


# Admin for Product Brand
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title',)
    list_filter = ('is_active',)


# Admin for Shop Product Categories
class ShopProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_category', 'ordering_number', 'is_active')
    search_fields = ('title',)
    list_filter = ('parent_category', 'is_active',)


# Admin for Cafe Product Categories
class CafeProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'shop', 'ordering_number', 'is_active')
    search_fields = ('title',)
    list_filter = ('is_active',)


# Admin for Features
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'feature_type', 'description')
    search_fields = ('title', 'description')


# Inline for Product Bundle Items
class ProductBundleItemInline(admin.TabularInline):
    model = ProductBundleItem
    extra = 1


# Admin for Product Bundle
class ProductBundleAdmin(admin.ModelAdmin):
    inlines = [ProductBundleItemInline]
    list_display = ['title', 'shop', 'bundle_price', 'is_active']
    list_filter = ['is_active', 'shop']


# Register ProductMediaFiles as a separate admin.
@admin.register(ProductMediaFiles)
class ProductMediaFilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'media_type', 'media_category', 'caption', 'created_date', 'is_global')
    list_filter = ('media_type', 'shop')
    search_fields = ('caption',)


# Registering Models with the Admin Site
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductBrand, ProductBrandAdmin)
admin.site.register(ShopProductCategory, ShopProductCategoryAdmin)
admin.site.register(CafeProductCategory, CafeProductCategoryAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(ProductFeature)
admin.site.register(ProductBundle, ProductBundleAdmin)
admin.site.register(ProductBundleItem)
