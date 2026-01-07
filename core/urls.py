"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="FeeCoffee API",
        default_version="v1",
        description="This is the APIs for FeeCoffee Project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="info@fee-coffee.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts_module.urls')),
    path('user-profiles/', include('user_module.urls')),
    path('shops/', include('shop_module.urls')),
    path('site-info/', include('site_module.urls')),
    path('cafe-marketplace/', include('cafe_market_module.urls')),
    path('shop-marketplace/', include('shop_market_module.urls')),
    path('products/', include('product_module.urls')),
    path('utils/', include('utils_module.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('sms/', include('auth_sms_module.urls')),
    path('articles/', include('article_module.urls')),
    path('image-collections/', include('media_collection_module.urls')),
    path('orders/', include('order_module.urls')),
    path('', include('home_module.urls')),

    # Api infrastructure
    path('swagger/api_output.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk')),]
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
