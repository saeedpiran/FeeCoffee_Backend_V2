from django.contrib import admin
from django.http import HttpRequest

from . import models


class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_title', 'is_active']
    list_editable = ['url_title', 'is_active']


class ArticleKeyWordsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    list_editable = ['is_active']


class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_title', 'parent', 'is_active']
    list_editable = ['url_title', 'parent', 'is_active']


class ArticleMediaFilesAdmin(admin.ModelAdmin):
    list_display = ['user', 'media_type', 'caption', 'created_date']
    list_filter = ['media_type', 'created_date']
    search_fields = ['caption']


class ArticleAdmin(admin.ModelAdmin):
    # Exclude created_date as it is auto-populated
    exclude = ['created_date']

    list_display = ['title', 'slug', 'is_active', 'author']
    list_editable = ['is_active']
    search_fields = ['title', 'short_description', 'text']

    # Enable autocomplete for the image field (one-to-one relation with ArticleMediaFiles)
    autocomplete_fields = ['image']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'text'),
        }),
        ('Media Files', {
            'fields': ('image',),
        }),
        ('Classification', {
            'fields': ('selected_categories', 'tags', 'key_words'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )

    def save_model(self, request: HttpRequest, obj: models.Article, form, change):
        if not change:
            obj.author = request.user  # Automatically assign the current user as author.
        return super().save_model(request, obj, form, change)


admin.site.register(models.ArticleTag, ArticleTagAdmin)
admin.site.register(models.ArticleKeyWords, ArticleKeyWordsAdmin)
admin.site.register(models.ArticleCategory, ArticleCategoryAdmin)
admin.site.register(models.ArticleMediaFiles, ArticleMediaFilesAdmin)
admin.site.register(models.Article, ArticleAdmin)

# from django.contrib import admin
# from django.utils import timezone
# from django.http import HttpRequest
#
# from .models import Article
# from . import models
#
#
# # Register your models here.
#
# class ArticleTagAdmin(admin.ModelAdmin):
#     list_display = ['title', 'url_title', 'is_active']
#     list_editable = ['url_title', 'is_active']
#
# class ArticleKeyWordsAdmin(admin.ModelAdmin):
#     list_display = ['title', 'is_active']
#     list_editable = ['is_active']
#
# class ArticleCategoryAdmin(admin.ModelAdmin):
#     list_display = ['title', 'url_title', 'parent', 'is_active']
#     list_editable = ['url_title', 'parent', 'is_active']
#
#
# class ArticleAdmin(admin.ModelAdmin):
#     exclude = ['created_date']
#     list_display = ['title', 'slug', 'is_active', 'author']
#     list_editable = ['is_active']
#
#     def save_model(self, request: HttpRequest, obj: Article, form, change):
#         if not change:
#             obj.author = request.user
#         if not obj.pk:
#             obj.create_date = timezone.now()
#         return super().save_model(request, obj, form, change)
#
#
#
# admin.site.register(models.ArticleTag, ArticleTagAdmin)
# admin.site.register(models.ArticleKeyWords, ArticleKeyWordsAdmin)
# admin.site.register(models.ArticleCategory, ArticleCategoryAdmin)
# admin.site.register(models.Article, ArticleAdmin)
#
#
