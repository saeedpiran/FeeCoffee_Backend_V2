from django.db import models
from django.utils import timezone


# Create your models here.


class CafeMarketBanner(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='عنوان بنر کافه ها')
    image = models.ImageField(upload_to='marketplace/cafes/banners', verbose_name='تصویر بنر کافه ها')
    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')
    is_active = models.BooleanField(default=True, null=True, verbose_name='فعال / غیرفعال')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = timezone.now()
        super(CafeMarketBanner, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'بنر کافه ها'
        verbose_name_plural = 'بنرهای کافه ها'
