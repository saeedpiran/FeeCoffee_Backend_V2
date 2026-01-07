# from django.contrib import admin
# from django.utils.html import format_html
#
# from accounts_module.models import UserMediaFiles
# from .models import UserProfile, StoredLocation
#
#
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_filter = ['is_active']
#     list_display = ['user_full_name', 'user_mobile_number', 'is_active']
#     list_editable = ['is_active']
#
#     def user_full_name(self, obj):
#         if obj.owner:
#             return f"{obj.owner.first_name} {obj.owner.last_name}"
#         return "-"
#
#     user_full_name.short_description = "User Full Name"
#
#     def user_mobile_number(self, obj):
#         if obj.owner:
#             return obj.owner.mobile
#         return "-"
#
#     user_mobile_number.short_description = "Mobile Number"
#
#
# @admin.register(StoredLocation)
# class StoredLocationAdmin(admin.ModelAdmin):
#     list_filter = ['title']
#     list_display = ['title', 'lat', 'long', 'state', 'city', 'address']
#
#
# class UserMediaFilesAdmin(admin.ModelAdmin):
#     list_display = ['user', 'media_type', 'caption', 'is_active', 'file_preview', 'created_date']
#     list_filter = ['media_type', 'is_active']
#
#     def file_preview(self, obj):
#         if obj.file:
#             return format_html('<img src="{}" width="50" height="50" />', obj.file.url)
#         return "No File"
#
#     file_preview.short_description = "Preview"
#
#
# # Unregister if already registered and then register with the new admin class.
# if UserMediaFiles in admin.site._registry:
#     admin.site.unregister(UserMediaFiles)
# admin.site.register(UserMediaFiles, UserMediaFilesAdmin)




from django.contrib import admin

from .models import UserProfile, StoredLocation


# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ['is_active']
    list_display = ['user_full_name', 'user_mobile_number', 'is_active']
    list_editable = ['is_active']


class StoredLocationAdmin(admin.ModelAdmin):
    list_filter = ['title']
    list_display = ['title', 'lat', 'long', 'state', 'city', 'address']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StoredLocation, StoredLocationAdmin)
