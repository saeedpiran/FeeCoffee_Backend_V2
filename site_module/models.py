from django.db import models


# Create your models here.

class SiteSetting(models.Model):
    author = models.CharField(max_length=200, null=True, blank=True, verbose_name='طراحی سایت')
    site_name = models.CharField(max_length=200, verbose_name='نام سایت')
    site_url = models.URLField(verbose_name='دامنه سایت')
    office_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='آدرس دفتر شرکت')
    office_phone = models.CharField(max_length=200, null=True, blank=True, verbose_name='تلفن دفتر شرکت')
    backup_phone = models.CharField(max_length=200, null=True, blank=True, verbose_name='تلفن پشتیبانی')
    fax = models.CharField(max_length=200, null=True, blank=True, verbose_name='فکس دفتر شرکت')
    email = models.CharField(max_length=200, null=True, blank=True, verbose_name='ایمیل شرکت')
    copy_right_text = models.TextField(verbose_name='متن کپی رایت')
    about_us_text = models.TextField(verbose_name='متن درباره ما')
    founder = models.CharField(max_length=200, null=True, verbose_name='بنیانگذار')
    site_logo = models.ImageField(upload_to='images/site_setting/logo', verbose_name='لوگو سایت')
    E_namad_code = models.TextField(blank=True, null=True, verbose_name='کد اینماد')
    instagram_link = models.URLField(null=True, verbose_name='لینک اینستاگرام')
    linkedin_link = models.URLField(null=True, verbose_name='لینک لینکدین')
    facebook_link = models.URLField(null=True, verbose_name='لینک فیسبوک')
    is_main_setting = models.BooleanField(verbose_name='تنظیمات اصلی')
    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')
    old_token_deletion = models.PositiveIntegerField(default=15, verbose_name='اعتبار توکن های اعضاء')

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات'

    def __str__(self):
        return self.site_name
