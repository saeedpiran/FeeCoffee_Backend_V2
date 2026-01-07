from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe

from .models import (
    ShopProfile,
    Shop,
    ShopMediaFiles,
    ShopOpenHours,
    ShopOpenDays,
    CafeTableQrCodes,
)


# Custom Admin for ShopProfile.
class ShopProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'owner', 'is_verified', 'city', 'state', 'owner_mobile']
    search_fields = ['shop__name', 'owner__first_name', 'owner__last_name', 'owner__mobile']
    list_filter = ['is_verified', 'city', 'state']
    list_editable = ['is_verified']
    readonly_fields = ['created_date', 'updated_date']

    def shop_name(self, obj):
        # Access the related Shop's name; if none exists, return a placeholder.
        return getattr(obj, 'shop', None).name if getattr(obj, 'shop', None) else "No Shop"

    shop_name.short_description = 'نام کافه/فروشگاه'

    def owner_mobile(self, obj):
        return obj.owner.mobile

    owner_mobile.short_description = 'شماره موبایل مالک'


# Custom Admin for Shop.
class ShopAdmin(admin.ModelAdmin):
    exclude = ['created_date']
    list_filter = ['shop_type', 'is_verified', 'name', 'created_date']
    list_display = ['name', 'shop_type', 'is_verified', 'created_date', 'updated_date']
    list_editable = ['is_verified']
    search_fields = ['name', 'shop_type']
    ordering = ['-created_date']  # Newest shops first
    readonly_fields = ['created_date', 'updated_date']
    actions = ['mark_verified', 'mark_unverified']

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Selected shops were marked as verified.")

    mark_verified.short_description = "Mark selected shops as verified"

    def mark_unverified(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Selected shops were marked as unverified.")

    mark_unverified.short_description = "Mark selected shops as unverified"

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Set created_date only for new objects.
            obj.created_date = timezone.now()
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # When editing an existing object, lock created_date.
            return self.readonly_fields + ['created_date']
        return self.readonly_fields


# Admin for ShopOpenDays with inline operating hours.
class ShopOpenHoursInline(admin.TabularInline):
    model = ShopOpenHours
    extra = 1  # Number of extra blank open hours fields


class ShopOpenDaysAdmin(admin.ModelAdmin):
    list_display = ['shop', 'open_day']
    list_filter = ['shop', 'open_day']
    inlines = [ShopOpenHoursInline]


# Custom Admin for ShopMediaFiles.
class ShopMediaFilesAdmin(admin.ModelAdmin):
    list_display = ('id','shop', 'media_type', 'caption', 'created_date','is_global', 'file_preview')
    list_filter = ('media_type', 'shop')
    search_fields = ('shop__name', 'caption')
    readonly_fields = ('created_date',)

    def file_preview(self, obj):
        if obj.file:
            # If file is an image, show a small preview.
            return mark_safe(f'<img src="{obj.file.url}" width="150" style="max-height: 150px;" />')
        return "No File"

    file_preview.short_description = 'File Preview'


# Admin for cafe table QR Codes.
class CafeTableQrCodesAdmin(admin.ModelAdmin):
    list_display = ['shop', 'shop_qr_code']
    list_filter = ['shop']
    search_fields = ['shop__name']


# Register models with custom admin.
admin.site.register(Shop, ShopAdmin)
admin.site.register(ShopProfile, ShopProfileAdmin)
admin.site.register(ShopMediaFiles, ShopMediaFilesAdmin)
admin.site.register(ShopOpenDays, ShopOpenDaysAdmin)
admin.site.register(ShopOpenHours)
admin.site.register(CafeTableQrCodes, CafeTableQrCodesAdmin)

# from django.contrib import admin
# from django.utils import timezone
#
# from .models import ShopProfile, Shop, ShopCertificateImage, ShopIdCardImage, ShopOpenHours, ShopOpenDays, \
#     CafeTableQrCodes
#
#
# class ShopCertificateImageInline(admin.TabularInline):
#     model = ShopCertificateImage
#     extra = 1  # Number of empty forms displayed by default
#
# class ShopIdCardImageInline(admin.StackedInline):
#     model = ShopIdCardImage
#     extra = 0  # Do not show any empty form by default
#
#
# # Custom Admin for ShopProfile
# class ShopProfileAdmin(admin.ModelAdmin):
#     inlines = [ShopCertificateImageInline, ShopIdCardImageInline]  # Certificates tied to ShopProfile
#     list_display = ['shop_name', 'owner', 'is_verified', 'city', 'state', 'owner_mobile']
#     search_fields = ['shop_name', 'owner__first_name', 'owner__last_name', 'owner__mobile']
#     list_filter = ['is_verified', 'city', 'state']
#     list_editable = ['is_verified']
#     readonly_fields = ['created_date', 'updated_date']
#
#     def shop_name(self, obj):
#         return getattr(obj.shop, 'name', "No Shop")
#     shop_name.short_description = 'نام کافه/فروشگاه'
#
#     def owner_mobile(self, obj):
#         return obj.owner.mobile
#     owner_mobile.short_description = 'شماره موبایل مالک'
#
#
# # Custom Admin for Shop
# class ShopAdmin(admin.ModelAdmin):
#     exclude = ['created_date']
#     list_filter = ['shop_type', 'is_verified', 'name', 'created_date']
#     list_display = ['name', 'shop_type', 'is_verified', 'created_date', 'updated_date']
#     list_editable = ['is_verified']
#     search_fields = ['name', 'shop_type']
#     ordering = ['-created_date']  # Newest shops first
#     readonly_fields = ['created_date', 'updated_date']
#     actions = ['mark_verified', 'mark_unverified']
#
#     def mark_verified(self, request, queryset):
#         queryset.update(is_verified=True)
#         self.message_user(request, "Selected shops were marked as verified.")
#
#     def mark_unverified(self, request, queryset):
#         queryset.update(is_verified=False)
#         self.message_user(request, "Selected shops were marked as unverified.")
#     mark_unverified.short_description = "Mark selected shops as unverified"
#
#     def save_model(self, request, obj, form, change):
#         if not obj.pk:  # Set `created_date` only for new objects
#             obj.created_date = timezone.now()
#         super().save_model(request, obj, form, change)
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # When editing an existing object
#             return tuple(self.readonly_fields) + ('created_date',)
#         return self.readonly_fields
#
#
#
# class ShopOpenHoursInline(admin.TabularInline):
#     model = ShopOpenHours
#     extra = 1  # Number of extra blank open hours fields
#
# class ShopOpenDaysAdmin(admin.ModelAdmin):
#     list_display = ['shop', 'open_day']
#     list_filter = ['shop', 'open_day']
#     inlines = [ShopOpenHoursInline]
#
# class CafeTableQrCodesAdmin(admin.ModelAdmin):
#     list_display = ['shop', 'shop_qr_code']
#     list_filter = ['shop']
#     search_fields = ['shop__name']
#
#
#
#
# # Register models with custom admin
# admin.site.register(Shop, ShopAdmin)
# admin.site.register(ShopProfile, ShopProfileAdmin)
# admin.site.register(ShopCertificateImage)
# admin.site.register(ShopIdCardImage)
# admin.site.register(ShopOpenDays, ShopOpenDaysAdmin)
# admin.site.register(ShopOpenHours)
# admin.site.register(CafeTableQrCodes, CafeTableQrCodesAdmin)
