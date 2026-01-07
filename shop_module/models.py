import os
import uuid
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.core.exceptions import ValidationError
from django.core.files import File
# from qrcode import QRCode
from django.db import models, transaction
from django.db.models import F, ExpressionWrapper, IntegerField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

from accounts_module.models import User
from core.settings import BASE_DIR

from site_module.models import SiteSetting


# Create your models here.
class ShopProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopprofile')
    latitude = models.DecimalField(max_digits=30, decimal_places=20, null=True, blank=True,
                                   verbose_name='عرض جغرافیایی')
    longitude = models.DecimalField(max_digits=30, decimal_places=20, null=True, blank=True,
                                    verbose_name='طول جغرافیایی')
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='کد پستی')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='پلاک')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='آدرس')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='شهر')
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name='استان')
    country = models.CharField(max_length=20, default='ایران', blank=True, verbose_name='کشور')
    is_complete = models.BooleanField(default=False, verbose_name='تکمیل/ناقص')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید/مردود')
    created_date = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name='تاریخ ثبت')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def clean(self):
        if self.latitude and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError("مقدار عرض جغرافیایی صحیح نیست.")
        if self.longitude and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError("مقدار طول جغرافیایی صحیح نیست.")

    def __str__(self):
        return str(self.owner)

    class Meta:
        verbose_name = 'پروفایل کافه/فروشگاه'
        verbose_name_plural = 'پروفایل کافه ها/فروشگاه ها'


# ------------------------------------------------------------------------------
# shop media files collection
def shop_media_files_upload_path(instance, filename):
    shop = str(instance.shop.id) if instance.shop else "global"
    folder = str(instance.media_type)
    return Path("images", "shops", shop, folder, filename)


class ShopMediaFiles(models.Model):
    """
        اگر میداتایپ و یا مدیا کتگوری تغییر کند حتماً سمت فرانت نیز نیاز به تغییر دارد و میبایست قبل از تغییر هماهنگی شود.
        """
    LOGO = 'logo'
    BANNERIMAGE = 'bannerimage'
    BANNERVIDEO = 'bannervideo'
    CERTIFICATE = 'certificate'
    IDCARD = 'idcard'
    MEDIA_TYPE_CHOICES = [
        (LOGO, 'لوگو'),
        (BANNERIMAGE, 'تصویر بنر'),
        (BANNERVIDEO, 'ویدیو بنر'),
        (CERTIFICATE, 'مجوز'),
        (IDCARD, 'کارت ملی'),
    ]
    shop = models.ForeignKey("Shop", on_delete=models.CASCADE, related_name='shop_media_files', null=True, blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to=shop_media_files_upload_path, null=True, blank=True, verbose_name='فایل')
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
        verbose_name = 'فایل مربوط به کافه/فروشگاه'
        verbose_name_plural = 'فایلهای مربوط به کافه/فروشگاه'


# ------------------------------------------------------------------
def shop_qr_code_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/images/shops/<shop_id>/logo/<filename>
    # return os.path.join('images', 'shops', str(instance.id), 'Qr_code', filename)
    if hasattr(instance, 'shop') and instance.shop is not None:
        return Path("images", "shops", str(instance.shop.id), "table_Qr_codes", filename)
    return Path("images", "shops", str(instance.id), "Qr_code", filename)


class Shop(models.Model):
    """
    create a shop profile with necessary information
    """
    CAFE = 'cafe'
    SHOP = 'shop'
    BOTH = 'both'
    SHOP_TYPE_CHOICES = [
        (CAFE, 'کافه'),
        (SHOP, 'فروشگاه'),
        (BOTH, 'هردو')
    ]
    H_TOMAN = 'h_toman'
    TOMAN = 'toman'
    MONETARY_UNIT_CHOICES = [
        (H_TOMAN, 'هزار تومان'),
        (TOMAN, 'تومان')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(ShopProfile, on_delete=models.CASCADE, default=None, related_name='shop')
    name = models.CharField(default='کافه/فروشگاه بی نام', max_length=100, verbose_name='نام فروشگاه')
    manager_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='نام مدیر داخلی')
    manager_mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name='موبایل مدیر داخلی')
    description = models.TextField(verbose_name='توضیحات')
    # logo = models.ImageField(upload_to=shop_logo_upload_path, default='default_images/shops/Fee.png', null=True,
    #                          blank=True,
    #                          verbose_name='لوگو')
    logo = models.OneToOneField(ShopMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name="shop_logo", verbose_name='لوگو کافه/فروشگاه')
    shop_url = models.URLField(max_length=200, null=True, blank=True, verbose_name='url کافه/فروشگاه')
    shop_qr_code = models.ImageField(upload_to=shop_qr_code_upload_path, null=True, blank=True, verbose_name='کد QR')
    number_of_tables = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name='تعداد میزهای کافه')
    # banner = models.ImageField(upload_to=shop_banner_upload_path, default='default_images/shops/banner.jpg', null=True,
    #                            blank=True,
    #                            verbose_name='بنر')
    banner = models.ManyToManyField(ShopMediaFiles, blank=True, related_name="shop_banner", verbose_name='بنر کافه')
    shop_type = models.CharField(max_length=10, choices=SHOP_TYPE_CHOICES, verbose_name='نوع کافه/فروشگاه')
    monetary_unit = models.CharField(max_length=10, default=TOMAN, choices=MONETARY_UNIT_CHOICES,
                                     verbose_name='واحد قیمت ها')
    id_card = models.OneToOneField(ShopMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="shop_owner_id_card", verbose_name='کارت ملی مالک')
    certificate = models.ManyToManyField(ShopMediaFiles, blank=True, related_name="shop_certificates",
                                         verbose_name='مجوزهای کافه/فروشگاه')
    free_delivery = models.BooleanField(default=False, verbose_name='ارسال رایگان')
    pickup = models.BooleanField(default=False, verbose_name='ارسال با فی کافی')
    phone_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='تلفن کافه/فروشگاه')
    id_card_upload = models.BooleanField(default=False, verbose_name='وضعیت بارگذاری کارت ملی')
    certificate_upload = models.BooleanField(default=False, verbose_name='وضعیت بارگذاری مجوز')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید/مردود')
    show_in_marketplace = models.BooleanField(default=False, verbose_name='نمایش در مارکت پلیس')
    sell_in_marketplace = models.BooleanField(default=False, verbose_name='فروش در مارکت پلیس')
    created_date = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name='تاریخ ثبت')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def __str__(self):
        return self.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Determine if this instance exists (and its table count) so we can detect changes.
        is_new = self.pk is None

        # Capture previous values for comparison if updating.
        old_number_of_tables = 0
        old_monetary_unit = None
        if not is_new:
            try:
                old_instance = Shop.objects.get(pk=self.pk)
                old_number_of_tables = old_instance.number_of_tables or 0
                old_monetary_unit = old_instance.monetary_unit
            except Shop.DoesNotExist:
                pass

        # First, let the base model save itself.
        super().save(*args, **kwargs)

        # If this is an update and the monetary unit has changed, update related product prices.
        if not is_new and old_monetary_unit and old_monetary_unit != self.monetary_unit:
            # Determine conversion factor based on the change.
            if old_monetary_unit == self.H_TOMAN and self.monetary_unit == self.TOMAN:
                conversion_factor = 1000
            elif old_monetary_unit == self.TOMAN and self.monetary_unit == self.H_TOMAN:
                conversion_factor = 0.001
            else:
                conversion_factor = 1

            # Retrieve the Product model using the apps registry to avoid circular imports.
            Product = apps.get_model('product_module', 'Product')

            # Bulk update related products (assuming related_name='products' in the Product model).
            # This will update all products including soft-deleted ones.
            Product.all_objects.filter(shop=self).update(
                price=ExpressionWrapper(F('price') * conversion_factor, output_field=IntegerField()),
                final_price=ExpressionWrapper(F('final_price') * conversion_factor, output_field=IntegerField())
            )

        if self.shop_type != self.SHOP:
            if not self.shop_url:
                self.generate_qr_code()

            # If the number of tables has changed, re-create the CafeTableQrCodes.
            new_table_count = self.number_of_tables or 0
            if new_table_count != old_number_of_tables:
                self.cafe_table_qr_codes.all().delete()
                for table_number in range(1, self.number_of_tables + 1):
                    qr_image = self.create_table_qr_code(table_number)
                    CafeTableQrCodes.objects.create(shop=self, shop_qr_code=qr_image)

    def generate_qr_code(self, table_no=0):

        table_no = f'table-no/{table_no}/'
        url = f'/cafe-menu/{self.id}/'
        # url = reverse('cafe_menu', kwargs={'shop_id': self.id}) # this should be change to right url of cafe menu
        main_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        base_url = main_setting.site_url if main_setting else "http://localhost"

        self.shop_url = f'{base_url}{url}'

        # Generate QR code for the shop
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,  # Adjust this value to change the size
            border=4,
        )
        qr_code_url = f'{self.shop_url}{table_no}'
        qr.add_data(qr_code_url)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(fill='black', back_color='white')

        # Save it to a BytesIO buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Save the image to the qr_code field
        self.shop_qr_code.save(f'qr_code.png', File(buffer), save=False)
        super().save()

    def create_table_qr_code(self, table_number):
        """
        Generate a QR code for the given table number and add the table number as text below the QR code.
        Returns a Django File object containing the image.
        """
        # Build the URL for this table's QR code
        table_suffix = f'table-no/{table_number}/'
        # Ensure the shop URL is available; generate if necessary.
        if not self.shop_url:
            self.generate_qr_code()

        # Generate the QR code using qrcode library.
        qr_url = f'{self.shop_url}{table_suffix}'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=3,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        # Create a Pillow image (RGB mode)
        qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

        # Prepare the text to display below the QR code.
        # persian_text = f"میز {table_number}"
        # reshaped_text = arabic_reshaper.reshape(persian_text)  # shapes characters correctly
        # bidi_text = get_display(reshaped_text)
        # text = bidi_text

        text = f"Table {table_number}"

        # Choose a font (you might need to adjust the font path/size according to your environment)
        try:
            # font = ImageFont.truetype("Vazir.ttf", 40)
            font_path = os.path.join(BASE_DIR, "static", "fonts", "ARIALBD.ttf")
            font = ImageFont.truetype(font_path, 100)
        except IOError:
            font = ImageFont.load_default()

        # Create a drawing context to measure text size.
        draw = ImageDraw.Draw(qr_img)
        # Use textbbox to get the bounding box of the text.
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Define separate margins for the text area.
        margin_top = 0  # Space between the QR code and the text (decreased space)
        margin_bottom = 60  # Space between the text and the bottom edge (increased space)

        # Determine the size of the new image: add extra space at the bottom for the text.
        qr_width, qr_height = qr_img.size
        new_height = qr_height + text_height + margin_top + margin_bottom
        new_img = Image.new("RGB", (qr_width, new_height), "white")

        # Paste the QR code at the top of the new image.
        new_img.paste(qr_img, (0, 0))

        # Center the text horizontally.
        text_x = (qr_width - text_width) // 2
        text_y = qr_height + margin_top
        # Draw the text on the new image.
        draw = ImageDraw.Draw(new_img)
        draw.text((text_x, text_y), text, fill="black", font=font)

        # Convert the combined image to 8-bit grayscale (L) mode
        new_img = new_img.convert("L")

        # Save the combined image to a BytesIO buffer.
        buffer = BytesIO()
        new_img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        # Return a Django File object that can be saved as an ImageField.
        image_filename = f'table_{table_number}_qr.png'
        return File(buffer, name=image_filename)

    class Meta:
        verbose_name = 'کافه/فروشگاه'
        verbose_name_plural = 'کافه ها/فروشگاه ها'


# -------------------------------------------------------------------------
# Table QR Codes
class CafeTableQrCodes(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='cafe_table_qr_codes')
    shop_qr_code = models.ImageField(upload_to=shop_qr_code_upload_path, null=True, blank=True,
                                     verbose_name='کد میزهای کافه QR')

    class Meta:
        verbose_name = 'qr کد میز کافه'
        verbose_name_plural = 'qr کدهای میزهای کافه'


# --------------------------------------------------------------------
# working hours
class ShopOpenDays(models.Model):
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SHOP_OPEN_DAYS_CHOICES = [
        (SATURDAY, 'شنبه'),
        (SUNDAY, 'یکشنبه'),
        (MONDAY, 'دوشنبه'),
        (TUESDAY, 'سه شنبه'),
        (WEDNESDAY, 'چهارشنبه'),
        (THURSDAY, 'پنجشنبه'),
        (FRIDAY, 'جمعه'),
    ]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='open_days')
    open_day = models.CharField(max_length=20, choices=SHOP_OPEN_DAYS_CHOICES, verbose_name='روزهای کاری')

    def __str__(self):
        return f" روز کاری روز {self.shop.name}"

    class Meta:
        verbose_name = 'روز کاری'
        verbose_name_plural = 'روزهای کاری'


class ShopOpenHours(models.Model):
    day = models.ForeignKey(ShopOpenDays, on_delete=models.CASCADE, related_name='open_hours')
    open_time = models.TimeField(verbose_name='ساعت شروع')
    close_time = models.TimeField(verbose_name='ساعت پایان')

    def __str__(self):
        return f" ساعات کاری روز {self.day.open_day} برای فروشگاه  {self.day.shop.name}"

    class Meta:
        verbose_name = 'ساعت کاری'
        verbose_name_plural = 'ساعات کاری'


# ---------------------------------------------------------------------
@receiver(post_save, sender=User)
def save_shop_profile(sender, instance, created, **kwargs):
    if created:
        if hasattr(instance, "user_type") and instance.user_type == "seller":
            # if instance.user_type == 'seller':
            ShopProfile.objects.create(owner=instance)


@receiver(post_save, sender=ShopProfile)
def save_shop(sender, instance, created, **kwargs):
    if created and not Shop.objects.filter(profile=instance).exists():
        Shop.objects.create(profile=instance)

# @receiver(post_save, sender=Shop)
# def save_shop_id_card(sender, instance, created, **kwargs):
#     if created:
#         try:
#             shop_profile = instance.profile  # Access the ShopProfile from the Shop instance
#             if not ShopIdCardImage.objects.filter(shop_profile=shop_profile).exists():
#                 ShopIdCardImage.objects.create(shop_profile=shop_profile)
#         except Exception as e:
#             # Log the error (use your preferred logging system)
#             print(f"Error creating ShopIdCardImage for Shop {instance.id}: {e}")
#

# @receiver(post_save, sender=Shop)
# def save_shop_certificates(sender, instance, created, **kwargs):
#     if created:
#         try:
#             shop_profile = instance.profile  # Access the ShopProfile from the Shop instance
#             if not ShopCertificateImage.objects.filter(shop_profile=shop_profile).exists():
#                 ShopCertificateImage.objects.create(shop_profile=shop_profile)
#         except Exception as e:
#             # Log the error (use your preferred logging system)
#             print(f"Error creating ShopCertificateImage for Shop {instance.id}: {e}")


# @receiver(post_save, sender=ShopCertificateImage)
# def reset_certificate_upload(sender, instance, **kwargs):
#     """Set certificate_upload to False when a ShopCertificateImage is saved."""
#     shop_profile = instance.shop_profile
#     if hasattr(shop_profile, 'shop'):  # Ensure the ShopProfile has an associated Shop
#         shop = shop_profile.shop
#         shop.certificate_upload = False
#         shop.save()


# @receiver(post_save, sender=ShopIdCardImage)
# def reset_id_card_upload(sender, instance, **kwargs):
#     """Set id_card_upload to False when a ShopIdCardImage is saved."""
#     shop_profile = instance.shop_profile
#     if hasattr(shop_profile, 'shop'):  # Ensure the ShopProfile has an associated Shop
#         shop = shop_profile.shop
#         shop.id_card_upload = False
#         shop.save()
