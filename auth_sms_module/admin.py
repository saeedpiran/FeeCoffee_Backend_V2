from django.contrib import admin

from .models import VerificationCode


# Register your models here.


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'code', 'created_at', 'expires_at', 'is_expired')
    search_fields = ('mobile', 'code')
    list_filter = ('created_at', 'expires_at')

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True  # Display as a boolean (Yes/No) in the admin interface
    is_expired.short_description = 'Expired'  # Custom column name in the admin interface


# Register the VerificationCode model with the custom admin settings
admin.site.register(VerificationCode, VerificationCodeAdmin)
