from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

router = DefaultRouter()
router.register('site_settings', views.SiteSettingsApiViewSet, basename='site_settings')

urlpatterns = [
    path('', include(router.urls)),
]
