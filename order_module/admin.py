from django.contrib import admin

from .models import Order, OrderDetail


# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'order_type', 'user', 'customer_name',
                    'table_number', 'is_confirmed', 'is_paid',
                    'created_date', 'updated_date', 'payment_date')
    list_filter = ('order_type', 'is_confirmed', 'is_paid', 'created_date')
    search_fields = ('customer_name', 'user__username', 'shop__name')


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'qty',
                    'final_price', 'created_date', 'updated_date')
    list_filter = ('created_date', 'updated_date')
    search_fields = ('order__id', 'product__name')
