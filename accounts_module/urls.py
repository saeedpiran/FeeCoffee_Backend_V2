from django.urls import path, include

from . import views

urlpatterns = [
    path('api/v1/', include('accounts_module.api.v1.urls')),


    # Render Based
    # --------------------------------------------------------------------------------------
    path('login/', views.LoginView.as_view(), name='login_page'),
    path('logout/', views.LogoutView.as_view(), name='logout_page'),
    # path('forget-pass/', views.ForgetPasswordView.as_view(), name='forget_password_page'),
    # path('reset-pass/', views.ResetPasswordView.as_view(), name='reset_password_page'),
    # path('signup/<str:type>', views.SendCodeView.as_view(), name='send_verification_code'),
    # path('verify_code/<str:type>', views.VerifyCodeView.as_view(), name='verify_code_signup'),
]
