# from django.contrib import admin
# from django.utils.html import format_html
#
# from .models import ImageCollectionCategory, ImageCollectionImage
#
#
# # Register your models here.
#
# # Inline admin for images linked to a category
# class ImageCollectionImageInline(admin.TabularInline):
#     model = ImageCollectionImage
#     extra = 0  # No extra blank forms by default
#     readonly_fields = ('image_preview',)  # Show image preview in the inline
#
#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
#         return "-"
#
#     image_preview.short_description = 'Preview'
#
#
# @admin.register(ImageCollectionCategory)
# class ImageCollectionCategoryAdmin(admin.ModelAdmin):
#     list_display = ('title', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('title',)
#     inlines = [ImageCollectionImageInline]  # Display associated images directly in category edit view
#
#
# @admin.register(ImageCollectionImage)
# class ImageCollectionImageAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'is_active', 'image_preview')
#     list_filter = ('is_active', 'category',)
#     search_fields = ('title',)
#     readonly_fields = ('image_preview',)  # Make the image preview read-only
#
#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
#         return "-"
#
#     image_preview.short_description = 'Preview'
