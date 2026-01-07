import os
import uuid
from pathlib import Path

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from multiselectfield import MultiSelectField
from rest_framework.exceptions import ValidationError

from shop_module.models import Shop


# Create your models here.
def generate_random_string():
    return get_random_string(20)


# ----------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Product media files collection
def product_media_files_upload_path(instance, filename):
    shop = str(instance.shop.id) if instance.shop else "global"
    folder = str(instance.media_type)
    return Path("images", "shops", shop, folder, filename)


class ProductMediaFiles(models.Model):
    """
    اگر میداتایپ و یا مدیا کتگوری تغییر کند حتماً سمت فرانت نیز نیاز به تغییر دارد و میبایست قبل از تغییر هماهنگی شود.
    """
    PRODUCT = 'product'
    CAFEPRODUCTCATEGORY = 'cafeproductcategory'
    MEDIA_TYPE_CHOICES = [
        (PRODUCT, 'تصویر محصول'),
        (CAFEPRODUCTCATEGORY, 'تصویر دسته بندی کافه'),
    ]
    HOT_DRINKS = 'hot_drinks'
    COLD_DRINKS = 'cold_drinks'
    CAKES = 'cakes'
    SHAKES = 'shakes'
    BEANS = 'beans'
    POWDER = 'powder'
    MEDIA_CATEGORY_CHOICES = [
        (HOT_DRINKS, 'انواع نوشیدنی گرم'),
        (COLD_DRINKS, 'انواع نوشیدنی خنک'),
        (CAKES, 'انواع کیک و دسر'),
        (SHAKES, 'انواع شیک'),
        (BEANS, 'دانه قهوه'),
        (POWDER, 'پودر قهوه'),
    ]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_media_files', null=True, blank=True)
    media_type = models.CharField(max_length=30, choices=MEDIA_TYPE_CHOICES)
    media_category = models.CharField(max_length=30, choices=MEDIA_CATEGORY_CHOICES, null=True, blank=True)
    file = models.FileField(upload_to=product_media_files_upload_path, null=True, blank=True, verbose_name='فایل')
    caption = models.CharField(max_length=255, blank=True, verbose_name='کپشن فایل')
    is_active = models.BooleanField(default=True, verbose_name='تأیید/مردود')
    created_date = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name='تاریخ ثبت')
    is_global = models.BooleanField(default=False, verbose_name="تصویر پیش‌فرض")
    optimized = models.BooleanField(default=False)  # New field to track processing

    def save(self, *args, **kwargs):
        if not self.file:
            raise ValidationError(f" باید یک {self.media_type} آپلود کنید. ")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shop} - {self.media_type} - {self.caption}"

    class Meta:
        verbose_name = 'فایل مربوط به محصول کافه/فروشگاه'
        verbose_name_plural = 'فایلهای مربوط به محصولات کافه/فروشگاه'


# ----------------------------------------------------------------------------------
# Brands
class ProductBrand(models.Model):
    """
    this class defines the brand for products
    """
    title = models.CharField(max_length=300, verbose_name='نام برند')
    en_title = models.CharField(default=generate_random_string, max_length=300,
                                verbose_name='عنوان انگلیسی')
    slug = models.SlugField(max_length=350, blank=True, allow_unicode=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برند ها'


# --------------------------------------------------------------------------------------
# Shop Products sub Categories
class ShopProductCategory(models.Model):
    """
    this is shop products categories
    """
    COFFEE = 'coffee'
    MACHINES = 'machines'
    CAPSULES = 'capsules'
    BREWING_TOOLS = 'brewing_tools'
    BARISTA_TOOLS = 'barista_tools'
    DRIP_BAGS = 'drip_bags'
    GRINDERS = 'grinders'
    COFFEE_MAKERS = 'coffee_makers'
    PARENT_CATEGORY_CHOICES = [
        (COFFEE, 'دانه/پودر'), (MACHINES, 'دستگاه ها'), (CAPSULES, 'کپسول ها'),
        (BREWING_TOOLS, 'تجهیزات دم آوری'), (BARISTA_TOOLS, 'تجهیزات باریستا'), (DRIP_BAGS, 'فوری/کیسه ای'),
        (GRINDERS, 'آسیاب ها'), (COFFEE_MAKERS, 'قهوه ساز ها')
    ]

    title = models.CharField(max_length=300, verbose_name='عنوان زیر دسته بندی')
    url_title = models.CharField(default=generate_random_string,
                                 max_length=300, verbose_name='عنوان زیر دسته بندی در url')
    slug = models.SlugField(max_length=350, blank=True, allow_unicode=True, verbose_name='عنوان در url')
    ordering_number = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    # shop = models.ForeignKey(Shop, related_name='product_category_shop',
    #                          on_delete=models.SET_NULL,
    #                          null=True, verbose_name='کافه/فروشگاه')
    # category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES, verbose_name='دسته بندی کافه/فروشگاهی')
    # category_type = models.ForeignKey(ProductType, related_name='product_category_type', on_delete=models.CASCADE, verbose_name='نوع دسته بندی (کافه/فروشگاه)')
    image = models.ImageField(upload_to='images/shop_product_category', null=True, blank=True,
                              default='default_images/product_category/product_category.jpg',
                              verbose_name='تصویر دسته بندی')
    # image = models.OneToOneField(ProductMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
    #                             related_name="shop_product_category_image", verbose_name='تصویر دسته بندی محصول فروشگاه')
    parent_category = MultiSelectField(
        choices=PARENT_CATEGORY_CHOICES,
        max_length=100,  # Adjust size as needed for the expected number of selections
        verbose_name='دسته بندی والد محصول',
        blank=True, null=True
    )
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shop_product_categories',
    #                             verbose_name='دسته بندی محصول فروشگاهی')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')

    # is_verified = models.BooleanField(verbose_name='تأیید شده / نشده')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی محصول فروشگاه'
        verbose_name_plural = 'دسته بندی محصولات فروشگاه'


# ---------------------------------------------------------------------
# Cafe product category
# def product_category_image_upload_path(instance, filename):
#     """
#     find the shop id in order to use it in upload to path in image
#     """
#     # Get the shop's ID or unknown_shop
#     shop_id = instance.shop.id if instance.shop else 'unknown_shop'
#
#     # Return the dynamic path with the original file name
#     return os.path.join(f"images/shops/{shop_id}/product_category", filename)


class CafeProductCategory(models.Model):
    """
    this is cafe products categories
    """
    CAFE_MENU = 'cafe_menu'
    BREAKFAST = 'breakfast'
    FOODS = 'foods'
    APPETIZERS = 'appetizers'
    CAFE_MENU_CATEGORY_TYPE_CHOICES = [
        (CAFE_MENU , 'منوی کافه'),
        (BREAKFAST , 'منوی صبحانه'),
        (FOODS , 'منوی غذا'),
        (APPETIZERS , 'منوی پیش غذا')
    ]
    title = models.CharField(max_length=300, verbose_name='عنوان زیر دسته بندی')
    url_title = models.CharField(max_length=300, null=True, blank=True,
                                 verbose_name='عنوان زیر دسته بندی در url')
    slug = models.SlugField(max_length=350, blank=True, allow_unicode=True, verbose_name='عنوان در url')
    ordering_number = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    shop = models.ForeignKey(Shop, related_name='product_category_shop',
                             on_delete=models.SET_NULL,
                             null=True, verbose_name='کافه')
    # image = models.ImageField(upload_to=product_category_image_upload_path, null=True, blank=True,
    #                           default='default_images/product_category/product_category.jpg',
    #                           verbose_name='تصویر دسته بندی')
    image = models.ForeignKey(ProductMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="cafe_product_category_image",
                                 verbose_name='تصویر دسته بندی محصول کافه')
    parent_category = models.CharField(default='cafe_menu',
                                       choices=CAFE_MENU_CATEGORY_TYPE_CHOICES,
                                       max_length=50,
                                       verbose_name='دسته بندی والد محصول کافه')
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cafe_product_categories',
    #                             verbose_name='دسته بندی محصول فروشگاهی')
    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیرفعال')
    is_deleted = models.BooleanField(default=False, verbose_name='حذف شده')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید  / مردود')

    def save(self, *args, **kwargs):
        # Automatically generate slug from title if not provided
        if not self.slug:
            # If url_title is not provided, generate one before creating the slug
            if not self.url_title:
                self.url_title = generate_random_string()
            self.slug = slugify(self.url_title, allow_unicode=True)
        super().save(*args, **kwargs)

    def clean(self):
        # Add validation for `parent_category`
        if self.parent_category not in dict(self.CAFE_MENU_CATEGORY_TYPE_CHOICES).keys():
            raise ValidationError("دسته بندی والد انتخابی معتبر نیست.")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی محصول کافه'
        verbose_name_plural = 'دسته بندی محصولات کافه'


# ------------------------------------------------------------------------------------------
# Product
class AliveProductManager(models.Manager):
    def get_queryset(self):
        # Only return products that are not soft-deleted.
        return super().get_queryset().filter(is_deleted=False)


def product_image_upload_path(instance, filename):
    """
    find the shop id in order to use it in upload to path in image
    """
    # Get the shop's ID or name
    shop_id = instance.product.shop.id
    # Return the dynamic path with the original file name
    return os.path.join(f"images/shops/{shop_id}/products", filename)


class Product(models.Model):
    CAFE = 'cafe'
    SHOP = 'shop'
    PRODUCT_TYPE_CHOICES = [
        (CAFE, 'منوی کافه'),
        (SHOP, 'محصول فروشگاهی')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300, verbose_name='نام محصول')
    en_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='نام انگیسی محصول')
    slug = models.SlugField(max_length=350, blank=True, allow_unicode=True, verbose_name='عنوان در url')
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, verbose_name='کافه/فروشگاه')
    ordering_number = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, verbose_name='نوع محصول کافه/فروشگاهی')
    image = models.ManyToManyField(ProductMediaFiles, blank=True, related_name="product_image",
                                   verbose_name='تصویر محصول')
    cafe_category = models.ForeignKey(
        CafeProductCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='دسته‌بندی محصولات کافه'
    )
    shop_category = models.ForeignKey(
        ShopProductCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='دسته‌بندی محصولات فروشگاه'
    )
    brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, verbose_name='برند', null=True, blank=True)
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت')
    discount = models.PositiveIntegerField(default=0,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)],
                                           verbose_name='درصد تخفیف')
    final_price = models.PositiveIntegerField(default=0, verbose_name='قیمت با تخفیف')
    short_description = models.CharField(max_length=360, db_index=True, null=True, verbose_name='توضیحات کوتاه')
    description = models.TextField(verbose_name='توضیحات اصلی', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ثبت')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')
    is_special = models.BooleanField(default=False, verbose_name='اسپشیالیتی')
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_deleted = models.BooleanField(default=False, verbose_name="حذف شده؟")
    show_in_shop = models.BooleanField(default=True, verbose_name='نمایش در پنل فروشگاه / عدم نمایش')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید شده / نشده')
    is_wholesale = models.BooleanField(default=False, verbose_name='فروش عمده')

    # Use the custom manager by default.
    objects = AliveProductManager()
    # In case you need to access all records (including soft-deleted ones)
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        # Override delete to perform a soft delete.
        self.is_deleted = True
        self.save()

    def clean(self):
        # Ensure only one category type is set
        if self.cafe_category and self.shop_category:
            raise ValidationError("هر محصول فقط در یکی از دسته بندی های محصول فروشگاه و یا منوی کافه می تواند باشد")

    def category(self):
        # Return the appropriate category based on the set field
        if self.cafe_category:
            return self.cafe_category.title
        elif self.shop_category:
            return self.shop_category.title
        return None

    category.short_description = "Category"

    def get_absolute_url(self):
        return reverse('', args=[self.id])

    def __str__(self):
        return f"{self.name} ({self.price})"

    def save(self, *args, **kwargs):
        # Calculate final price based on price and discount.
        # Using integer arithmetic; adjust as needed if you require floats.
        self.final_price = self.price - (self.price * self.discount // 100)
        # Set created_date if not already set (this code is already in your save)
        if not self.created_date:
            self.created_date = timezone.now()
        # Call the superclass's save method to continue saving.
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def get_images_urls(self):
        # Iterate over the many-to-many relation using the field name `image`
        # and return a list of uploaded file URLs.
        return [img.file.url for img in self.image.all()]

    def get_first_image_url(self):
        first_image = self.image.all().first()
        if first_image:
            return first_image.file.url
        return None


# --------------------------------------------------------------------------------
class Feature(models.Model):
    """
    this class defines the features of products which related to the product type
    """
    CAFE = 'cafe'
    SHOP = 'shop'
    FEATURE_TYPE_CHOICES = [
        (CAFE, 'منوی کافه'),
        (SHOP, 'محصول فروشگاهی')
    ]
    title = models.CharField(max_length=255, null=True, verbose_name='عنوان ویژگی')
    url_title = models.CharField(max_length=255, null=True, verbose_name='عنوان انگلیسی ویژگی')
    feature_type = models.CharField(max_length=10, choices=FEATURE_TYPE_CHOICES, verbose_name='نوع ویژگی کافه/فروشگاهی')
    slug = models.SlugField(max_length=350, blank=True, allow_unicode=True, verbose_name='عنوان در url')
    description = models.TextField(blank=True, verbose_name='توضیحات ویژگی')
    is_additive = models.BooleanField(default=False, verbose_name='افزودنی')

    # product = models.ForeignKey(Product, related_name='features', on_delete=models.CASCADE, verbose_name='محصول')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی های محصول'


class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_features',
                                verbose_name='محصول')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='features',
                                verbose_name='ویژگی')
    # feature_value = models.ForeignKey(FeatureValues, on_delete=models.CASCADE, related_name='product_feature_values',verbose_name='مقدار ویژگی')
    feature_value = models.CharField(max_length=255, null=True, verbose_name='مقدار ویژگی')
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت')
    final_price = models.PositiveIntegerField(default=0, verbose_name='قیمت با تخفیف')

    def __str__(self):
        return f"{self.product.name} - {self.feature.title}: {self.feature_value}"

    def save(self, *args, **kwargs):
        if not self.feature.is_additive:
            # Compute the discount amount based on the feature's price
            discount_amount = (self.price * self.product.discount) // 100
            self.final_price = self.price - discount_amount
        else:
            # Optional: if is_additive is True, you might want to simply add the feature's price
            # to the product's final price. Adjust the logic according to your business rules.
            self.final_price = self.price

        super(ProductFeature, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'مقدار ویژگی محصول'
        verbose_name_plural = 'مقادیر ویژگی های محصول'


class ProductBundle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(Shop, related_name='bundles', on_delete=models.CASCADE, verbose_name='کافه/فروشگاه')
    title = models.CharField(max_length=300, verbose_name='عنوان پیشنهاد ویژه')
    products = models.ManyToManyField(Product, through='ProductBundleItem', related_name='bundles',
                                      verbose_name='محصولات بسته')
    bundle_price = models.IntegerField(verbose_name='قیمت بسته')
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید شده / نشده')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'باندل محصول'
        verbose_name_plural = 'باندل محصولات'

    def get_image_url(self):
        image_url = []
        for product in self.products.all():
            image_url.append(product.get_first_image_url())
        return image_url[0] if image_url else None


class ProductBundleItem(models.Model):
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name='bundle_items',
                               verbose_name='باندل')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bundle_items', verbose_name='محصول')
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')

    def __str__(self):
        return f"{self.bundle.title} - {self.product.name}"

    class Meta:
        verbose_name = 'مورد باندل محصول'
        verbose_name_plural = 'موارد باندل محصولات'


# @receiver(pre_save, sender=ProductParentCategory)
# def update_slug(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.url_title)
#
# @receiver(pre_save, sender=ProductType)
# def update_slug(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.url_title)
#
# @receiver(pre_save, sender=ProductCategory)
# def update_slug(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.url_title)

@receiver(post_save, sender=ProductBrand)
def update_brand_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        instance.slug = slugify(instance.en_title)
        instance.save()


@receiver(pre_save, sender=Product)
def update_product_slug(sender, instance, **kwargs):
    if not instance.slug:
        if not instance.en_name:
            instance.en_name = generate_random_string()
        instance.slug = slugify(instance.en_name)
    # instance.is_active = True

@receiver(post_save, sender=Product)
def update_product_features(sender, instance, created, **kwargs):
    features = instance.product_features.all()
    if features.exists():
        for feature in features:
            feature.save()  # Recalculates final_price in ProductFeature.save()

# @receiver(pre_save, sender=CafeProductCategory)
# def update_cafe_product_category_slug(sender, instance, **kwargs):
#     if not instance.slug:
#         print(f"Before update, url_title : {instance.url_title}")
#         if not instance.url_title:
#             instance.url_title = generate_random_string()
#             print(f"Generated url_title : {instance.url_title}")
#         instance.slug = slugify(instance.url_title)
#         print(f"Generated slug : {instance.slug}")


# @receiver(post_save, sender=Product)
# def product_default_image(sender, instance, created, **kwargs):
#     """
#     Automatically assign a default image to the product if no images exist
#     when the product is created.
#     """
#     if created and not instance.images.exists():  # Check if product has no images
#         ProductImage.objects.create(
#             product=instance,
#             image='default_images/products/product.jpg',  # Path to default image
#             description='Default product image'
#         )

@receiver(pre_save, sender=Feature)
def update_slug(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.url_title)

# @receiver(pre_save, sender=FeatureValues)
# def update_slug(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.en_name)
