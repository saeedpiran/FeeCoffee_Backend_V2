from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

router = DefaultRouter()
router.register('products', views.ShopMarketIndexViewSet, basename='shop-market')

urlpatterns = [
    path('shop-marketplace-banners/', views.ShopBannerList.as_view(), name='shop_marketplace_banner_list'),
    path('shop-marketplace-banner/<int:pk>/', views.ShopBannerDetail.as_view(), name='shop_marketplace_banner_delete'),
    path('', include(router.urls)),
]
