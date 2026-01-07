from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api-v1'

router = DefaultRouter()
router.register('stored-locations', views.StoredLocationViewSet, basename='stored_location')

# user avatar manager
# router.register(r'user-avatar', views.UserAvatarViewSet, basename='user_avatar')

urlpatterns = [
    # user profile
    path('user-profile/', views.UserProfileApiView.as_view(), name='user_profile'),

    # User avatar
    # path('profile/avatar/', views.AvatarRetrieveUpdateAPIView.as_view(), name='avatar_update'),
    path('', include(router.urls)),
]
