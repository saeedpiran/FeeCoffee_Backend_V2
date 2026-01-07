from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

router = DefaultRouter()

# User Media file Management
router.register(r'user-avatar', views.UserAvatarUploadViewSet, basename='user_avatar')

urlpatterns = [
    # registration check
    path('registration-check/', views.RegistrationCheckApiView.as_view(), name='registration_check'),

    # registration second step
    path('registration/', views.RegistrationApiView.as_view(), name='registration'),

    # -----------------------------------------------------------------------------------------------
    # change password
    path('change-password/', views.ChangePasswordApiView.as_view(), name='change_password'),

    # ---------------------------------------------------------------------------------------------------
    # forget password check
    path('forget-password-check/', views.ForgetPassCheckApiView.as_view(), name='forget_password_check'),

    # forget password second step
    path('forget-password/', views.ForgetPassApiView.as_view(), name='forget_password'),
    # -----------------------------------------------------------------------------------------

    # login Token
    path('token/login/', views.CustomObtainAuthToken.as_view(), name='login_token'),

    # logout token
    path('token/logout/', views.CustomDiscardAuthToken.as_view(), name='logout_token'),

    # User full name and type
    path('user-basic-data/', views.UserFullNameAndTypeAPIView.as_view(), name='user_basic_data'),

    # rooters
    path('', include(router.urls)),

    # ======================================================================================
    # # Login JWT
    # path('jwt/login/', views.CustomTokenObtainPairView.as_view(), name='create_jwt'),
    #
    # # path('jwt/refresh/', TokenRefreshView.as_view(), name='refresh_jwt'),
    # path('jwt/verify/', TokenVerifyView.as_view(), name='verify_jwt'),
    #
    # # logout
    # path('logout/', views.LogoutView.as_view(), name='logout'),
]
