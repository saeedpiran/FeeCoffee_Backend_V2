from django.db import models
from django.utils import timezone


# Create your models here.


class VerificationCode(models.Model):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='موبایل')
    code = models.CharField(max_length=6, verbose_name='کد اعتبارسنجی')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='زمان ایجاد')
    expires_at = models.DateTimeField(verbose_name='زمان انقضا')

    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        verbose_name = 'کد اعتبارسنجی'
        verbose_name_plural = 'کدهای اعتبارسنجی'
