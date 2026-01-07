from django.urls import path, include

from cafe_market_module import views

urlpatterns = [

    path('api/v1/', include('cafe_market_module.api.v1.urls')),
]
