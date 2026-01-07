from django.urls import path,include

from shop_market_module import views


urlpatterns = [
    path('api/v1/', include('shop_market_module.api.v1.urls')),
]
