from django.utils import timezone


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from order_module.api.v1.serializers import OrderSerializer, OrderDetailSerializer
from order_module.models import Order, OrderDetail
from shop_module.models import Shop



