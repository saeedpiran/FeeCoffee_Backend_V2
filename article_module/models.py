import os
import uuid
from pathlib import Path

from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts_module.models import User


# Create your models here.
# ------------------------------------------------------------------------------
# Product media files collection
def article_media_files_upload_path(instance, filename):
    user = str(instance.user.id)
    folder = str(instance.media_type)
    return Path("images", "users", user, folder, filename)


class ArticleMediaFiles(models.Model):
    ARTICLE = 'article'
    MEDIA_TYPE_CHOICES = [
        (ARTICLE, 'تصویر مقاله'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='article_media_files')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default=ARTICLE)
    file = models.FileField(upload_to=article_media_files_upload_path, null=True, blank=True, verbose_name='فایل')
    caption = models.CharField(max_length=255, blank=True, verbose_name='کپشن فایل')
    is_active = models.BooleanField(default=True, verbose_name='تأیید/مردود')
    created_date = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name='تاریخ ثبت')
    optimized = models.BooleanField(default=False)  # New field to track processing

    def save(self, *args, **kwargs):
        if not self.file:
            raise ValidationError(f" باید یک {self.media_type} آپلود کنید. ")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.media_type} - {self.caption}"

    class Meta:
        verbose_name = 'فایل مربوط به مقاله'
        verbose_name_plural = 'فایلهای مربوط به مقالات'


# ------------------------------------------------------------------------

class ArticleTag(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان برچسب')
    url_title = models.CharField(max_length=200, unique=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیر فعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب ها'


class ArticleKeyWords(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان کلمه کلیدی')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیر فعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'کلمه کلیدی'
        verbose_name_plural = 'کلمات کلیدی'


class ArticleCategory(models.Model):
    parent = models.ForeignKey('ArticleCategory', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name='دسته بندی والد')
    title = models.CharField(max_length=200, verbose_name='عنوان دسته بندی')
    url_title = models.CharField(max_length=200, unique=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیر فعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی مقاله'
        verbose_name_plural = 'دسته بندی های مقاله'


def get_article_image_upload_path(instance, filename):
    # Get the current date
    current_date = timezone.now().strftime('%Y-%m-%d')
    # Create the path based on the date
    return os.path.join('images', 'articles', current_date, filename)


class Article(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان مقاله')
    # url_title = models.SlugField(max_length=400, unique=True, verbose_name='عنوان در url')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='عنوان در url')
    # image = models.ImageField(upload_to=get_article_image_upload_path, verbose_name='تصویر مقاله',default='default_images/articles/article.jpg')
    image = models.OneToOneField(ArticleMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="article_image",
                                 verbose_name='تصویر مقاله')
    short_description = models.TextField(verbose_name='توضیح کوتاه')
    text = models.TextField(verbose_name='متن مقاله')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیر فعال')
    selected_categories = models.ManyToManyField(ArticleCategory, verbose_name='دسته بندی ها')
    tags = models.ManyToManyField(ArticleTag, verbose_name='برچسب ها')
    key_words = models.ManyToManyField(ArticleKeyWords, verbose_name='کلمات کلیدی')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='نویسنده', null=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

# @receiver(pre_save, sender=Article)
# def update_slug(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.url_title)
