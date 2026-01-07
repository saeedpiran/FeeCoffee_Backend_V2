from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import User, UserMediaFiles


class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('mobile',)

    list_display = (
        'mobile',
        'first_name',
        'last_name',
        'user_type',
        'is_superuser',
        'is_active',
        'is_verified',
    )

    list_filter = (
        'mobile',
        'user_type',
        'is_active',
        'is_superuser',
        'is_verified',
    )

    search_fields = ('mobile', 'first_name', 'last_name', 'id_number')

    readonly_fields = ('created_date', 'updated_date', 'last_login')

    fieldsets = (
        (None, {
            'fields': ('mobile', 'password')
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'id_number',
                'user_type',
                'avatar'
            )
        }),
        ('Referral', {
            'fields': (
                'introducer',
                'introduction_url'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_verified',
                'groups',
                'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': (
                'last_login',
                'created_date',
                'updated_date'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'mobile',
                'password1',
                'password2',
                'user_type',
                'is_active',
                'is_staff',
                'is_superuser',
                'is_verified'
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_date = timezone.now()
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)


class UserMediaFilesAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_type', 'caption', 'created_date')
    list_filter = ('media_type', 'created_date')
    search_fields = ('user__first_name', 'user__last_name', 'caption')


admin.site.register(UserMediaFiles, UserMediaFilesAdmin)

# from django.contrib import admin
# from django.utils import timezone
# from django.contrib.auth.admin import UserAdmin
# from .models import User
# from rest_framework.authtoken.models import Token
#
#
# # Register your models here.
#
#
# class CustomUserAdmin(UserAdmin):
#     model = User
#     exclude = ['created_date']
#     list_display = ('mobile', 'first_name','last_name' ,  'user_type', 'is_superuser', 'is_active')
#     list_filter = ('mobile', 'is_active')
#     list_editable = ('user_type',)
#     search_fields = ('mobile',)
#     ordering = ('mobile',)
#     fieldsets = (  # نمایش داده ها
#         ('کاربر',{
#             "fields": (
#                 'first_name', 'last_name', 'user_type', 'avatar'
#             )
#         }),
#         ('احراز هویت', {
#             "fields": (
#                 'mobile', 'password'
#             ),
#         }),
#         ('مجوزها', {
#             "fields": (
#                 'is_staff', 'is_active', 'is_superuser'
#             ),
#         }),
#         ('گروه مجوزها', {
#             "fields": (
#                 'groups', 'user_permissions'
#             ),
#         }),
#         ('تاریخ های مهم', {
#             "fields": (
#                 'last_login',
#             ),
#         }),
#     )
#     add_fieldsets = (  # وارد شدن داده ها
#         ('Authentication', {
#             "classes": ('wide',),
#             'fields': ('mobile', 'password1', 'password2', 'user_type', 'is_staff', 'is_active', 'is_superuser')
#         }),
#     )
#
#     def save_model(self, request, obj, form, change):
#         if not obj.pk:
#             obj.created_date = timezone.now()
#         super().save_model(request, obj, form, change)
#
# # class TokenAdmin(admin.ModelAdmin):
# #     list_display = ('key', 'user', 'created')
# #     search_fields = ('key', 'user__mobile')
# #     list_filter = ('created',)
# #
# #     # Customizing the verbose name
# #     verbose_name = "توکن"
# #     verbose_name_plural = "توکن ها"
# #
#
#
#
# admin.site.register(User, CustomUserAdmin)
#
# # # Check if the Token model is already registered
# # if Token in admin.site._registry:
# #     admin.site.unregister(Token)
# #
# # # Register the Token model with the custom TokenAdmin
# # admin.site.register(Token, TokenAdmin)
