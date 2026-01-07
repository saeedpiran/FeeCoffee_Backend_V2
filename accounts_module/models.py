import uuid
from pathlib import Path

from decouple import config
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, mobile, password=None, **extra_fields):
        """
        create user here
        """
        if not mobile:
            raise ValueError("موبایل باید وارد شود")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        """
        Create Superuser here
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('برای ابرکاربر باید is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('برای ابرکاربر باید is_superuser = True')
        return self.create_user(mobile, password, **extra_fields)

    def get_by_natural_key(self, mobile):
        return self.get(mobile=mobile)


# def avatar_upload_path(instance, filename):
#     # File will be uploaded to MEDIA_ROOT/images/users/<user_id>/avatar/<filename>
#     return os.path.join('images', 'users', str(instance.id), 'avatar', filename)

# def user_id_card_img_upload_path(instance, filename):
#     # File will be uploaded to MEDIA_ROOT/images/users/<user_id>/id_card/<filename>
#     return os.path.join('images', 'users', str(instance.id), 'id_card', filename)


# ------------------------------------------------------------------------------
# User media files collection
# def user_media_files_upload_path(instance, filename):
#     # Check if the user is neither a superuser nor a staff member.
#     if not instance.user.is_superuser and not instance.user.is_staff:
#         user = str(instance.user.id)
#     else:
#         # Define a custom folder for superusers/staff if needed.
#         user = f"Admin {instance.uer.id}"
#     folder = str(instance.media_type)
#     return Path("images", "users", user, folder, filename)

def user_media_files_upload_path(instance, filename):
    # If no user is associated (e.g., global file upload), use a default folder.
    if not instance.user:
        user = "global"
    # Check if the user is neither a superuser nor a staff member.
    elif not instance.user.is_superuser and not instance.user.is_staff:
        user = str(instance.user.id)
    else:
        # Use a specific folder for superusers/staff.
        user = f"admin_{instance.user.id}"

    folder = str(instance.media_type)
    return Path("images", "users", user, folder, filename)


class UserMediaFiles(models.Model):
    """
        اگر میداتایپ و یا مدیا کتگوری تغییر کند حتماً سمت فرانت نیز نیاز به تغییر دارد و میبایست قبل از تغییر هماهنگی شود.
        """
    AVATAR = 'avatar'
    MEDIA_TYPE_CHOICES = [
        (AVATAR, 'آواتار'),
    ]
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='user_media_files', null=True, blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default=AVATAR)
    file = models.FileField(upload_to=user_media_files_upload_path, null=True, blank=True, verbose_name='فایل')
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
        return f"{self.user} - {self.media_type} - {self.caption}"

    class Meta:
        verbose_name = 'فایل مربوط به کاربر'
        verbose_name_plural = 'فایلهای مربوط به کاربران'


# ---------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user Model for app
    """
    SELLER = 'seller'
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    USER_TYPE_CHOICES = [
        (SELLER, 'Seller'),
        (CUSTOMER, 'Customer'),
        (ADMIN, 'admin')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile = models.CharField(db_index=True, max_length=20, unique=True, verbose_name='موبایل')
    introducer = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='introduced_users',  # Allows reverse relation, i.e., fetching users introduced by this user
        verbose_name='معرف'  # Persian for "Introducer"
    )
    introduction_url = models.URLField(max_length=300, blank=True, verbose_name='لینک معرفی')
    first_name = models.CharField(max_length=100, null=True, blank=True, default='کاربر', verbose_name='نام')
    last_name = models.CharField(max_length=100, null=True, blank=True, default='نامشخص',
                                 verbose_name='نام خانوادگی')
    id_number = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد ملی')
    # avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True, default='default_images/avatar/user_avatar.png',
    #                           verbose_name='تصویر کاربر')
    avatar = models.ForeignKey(UserMediaFiles, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="user_avatars",
                                  verbose_name='آواتار کاربر')
    # id_card_image = models.ImageField(upload_to=user_id_card_img_upload_path, null=True, blank=True,
    #                                   verbose_name='تصویر کارت ملی کاربر')
    is_superuser = models.BooleanField(default=False, verbose_name='ابرکاربر')
    is_staff = models.BooleanField(default=False, verbose_name='کارمند')
    is_active = models.BooleanField(default=False, verbose_name='فعال/غیرفعال')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید شده/تأیید نشده')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer', null=True, blank=True,
                                 verbose_name='نوع کاربر')

    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return f"{self.first_name} - {self.last_name} - {self.mobile}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=User)
def set_introduction_url(sender, instance, created, **kwargs):
    if created:  # Ensure the signal runs only when a new user is created
        # Get the domain from the .env file
        base_url = config('DOMAIN', default='https://fee-coffee.com')

        # Generate the introduction URL
        unique_identifier = str(instance.id)  # Use user ID for uniqueness
        introduction_url = f"{base_url}/signup?user_type=customer&introducer={unique_identifier}"
        # print(introduction_url)

        # Set the introduction_url field
        instance.introduction_url = introduction_url
        instance.save()  # Save the changes to the database
