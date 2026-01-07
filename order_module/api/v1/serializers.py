from rest_framework import serializers

from order_module.models import OrderDetail, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'shop', 'order_type', 'user', 'customer_name', 'table_number',
            'is_confirmed', 'is_paid', 'created_date', 'updated_date', 'payment_date'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date']


class OrderDetailSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'product', 'qty', 'final_price', 'created_date', 'updated_date', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
