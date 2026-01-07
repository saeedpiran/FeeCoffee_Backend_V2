import logging
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import status

from accounts_module.models import User
from utils_module.api.v1.views import NeshanReverseGeocodingAPIView


# Create your models here.

class StoredLocation(models.Model):
    user_profile = models.ForeignKey('UserProfile', related_name='stored_locations', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='')
    lat = models.FloatField()
    long = models.FloatField()
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name='استان')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='شهر')
    address = models.CharField(max_length=256, null=True, blank=True, verbose_name='آدرس')

    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مکان ذخیره شده'
        verbose_name_plural = 'مکان ها ذخیره شده'


logger = logging.getLogger(__name__)


# Define the signal handler outside the class
@receiver(post_save, sender=StoredLocation)
def update_location_data(sender, instance, created, **kwargs):
    if created:
        if instance.lat and instance.long:
            data, state, city, detailed_address, status_code = NeshanReverseGeocodingAPIView.get_location_data(
                instance.lat, instance.long)

            if status_code == status.HTTP_200_OK:
                instance.address = detailed_address
                instance.state = state
                instance.city = city
                instance.save()
            else:
                # Handle the error response accordingly
                logger.error(
                    f"Failed to update location data for StoredLocation {instance.id}: status_code {status_code}")

# ---------------------------------------------------------------------------
class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='فعال / غیرفعال')
    # stored_locations = models.TextField(null=True, blank=True,
    #                                     verbose_name='آدرسهای ذخیره شده')  # Store list as JSON string
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='کد پستی')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='پلاک')
    address = models.CharField(max_length=255, verbose_name='آدرس')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='شهر')
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name='استان')
    country = models.CharField(max_length=20, default='ایران', null=True, blank=True, verbose_name='کشور')

    created_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def user_full_name(self):
        return self.owner.get_full_name()

    user_full_name.short_description = 'نام و نام خانوادگی'

    def user_mobile_number(self):
        return self.owner.mobile

    user_mobile_number.short_description = 'شماره موبایل'

    def __str__(self):
        return self.owner.get_full_name()

    class Meta:
        verbose_name = 'کاربر خریدار'
        verbose_name_plural = 'کاربران خریدار'


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'customer':
            UserProfile.objects.create(owner=instance)
