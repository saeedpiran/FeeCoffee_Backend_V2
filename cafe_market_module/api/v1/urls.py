from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

router = DefaultRouter()
router.register('nearby-cafes', views.CafeMarketIndexViewSet, basename='cafe_market')

urlpatterns = [
    path('cafe-marketplace-banners/', views.CafeBannerList.as_view(), name='cafe_marketplace_banner_list'),
    path('cafe-marketplace-banner/<int:pk>/', views.CafeBannerDetail.as_view(), name='cafe_marketplace_banner_delete'),
    path('', include(router.urls)),
]

# urlpatterns = [
#     path('api/v1/nearby-cafes/', views.CafeMarketIndexView.as_view(), name='cafe_market'),
# ]
