from django.contrib import admin
from django.utils import timezone

from . import models


# Register your models here.

class CafeMarketBannerAdmin(admin.ModelAdmin):
    list_filter = ['is_active']
    list_display = ['title', 'is_active', 'created_date']
    list_editable = ['is_active']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_date = timezone.now()
        super().save_model(request, obj, form, change)


admin.site.register(models.CafeMarketBanner, CafeMarketBannerAdmin)
