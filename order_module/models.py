import uuid

from django.db import models

from accounts_module.models import User
from product_module.models import Product
from shop_module.models import Shop


# Create your models here.


class Order(models.Model):
    INTERNAL = 'internal'
    EXTERNAL = 'external'
    ORDER_TYPE_CHOICES = [
        (INTERNAL, 'سفارش داخلی'),
        (EXTERNAL, 'سفارش خارجی')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(Shop, related_name='internal_temp_orders',
                             on_delete=models.CASCADE, verbose_name='کافه/فروشگاه')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES,
                                  default='internal', verbose_name='نوع سفارش داخلی/خارجی')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name='کاربر')
    customer_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام مشتری')
    table_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='شماره میز')
    is_confirmed = models.BooleanField(default=False, verbose_name='تایید شده / نشده')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده / نشده')

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'سبد سفارش'
        verbose_name_plural = 'سبدهای سفارش'


class OrderDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='order_details',
                              on_delete=models.CASCADE, verbose_name='جزئیات سفارش موقت')
    product = models.ForeignKey(Product, related_name='internal_temp_order_products',
                                on_delete=models.PROTECT, verbose_name='محصول')
    qty = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    final_price = models.IntegerField(null=True, blank=True, verbose_name='قیمت نهایی تکی محصول')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی')

    def save(self, *args, **kwargs):
        if self.final_price is None:
            self.final_price = self.product.price
        super().save(*args, **kwargs)

    def get_total_price(self):
        return self.qty * self.product.price

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name = 'جزئیات سفارش'
        verbose_name_plural = 'لیست جزئیات سفارش'
