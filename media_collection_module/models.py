import os

from django.db import models


# Create your models here.
class ImageCollectionCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان دسته بندی مجموعه')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیرفعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی مجموعه'
        verbose_name_plural = 'دسته بندی های مجموعه'


def get_collection_image_upload_path(instance, filename):
    if instance.category:
        category_str = str(instance.category)
    else:
        category_str = 'uncategorized'
    return os.path.join('images', 'image_collections', category_str, filename)


class ImageCollectionImage(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان تصویر')
    image = models.ImageField(upload_to=get_collection_image_upload_path,
                              verbose_name='تصویر')
    category = models.ForeignKey(ImageCollectionCategory, on_delete=models.CASCADE,
                                 verbose_name='دسته بندی', null=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیرفعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'تصویر مجموعه'
        verbose_name_plural = 'تصاویر مجموعه'
