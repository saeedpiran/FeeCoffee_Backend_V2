from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('order_module.api.v1.urls')),
]
