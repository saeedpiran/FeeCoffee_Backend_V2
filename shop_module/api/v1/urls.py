from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

# router = DefaultRouter()
# router.register('product', ProductViewSet, basename='product')

router = DefaultRouter()
# router.register(r'shop/certificates', views.ShopCertificateImageViewSet, basename='shop_certificate')

# admin for shops
# router.register(r'admin/shops', views.ShopAdminViewSet, basename='admin_shop')

# shop File manager
router.register(r'shop-media-files', views.ShopMediaFilesViewSet, basename='shop_media_files')

urlpatterns = [

    # shop dashboard
    path('shop-dashboard/', views.ShopDashboardView.as_view(), name='shop_dashboard'),

    # shop profile
    path('shop-profile/', views.ShopProfileApiView.as_view(), name='shop_profile'),

    # Shop Profile Is Complete Status
    path('shop-profile/complete-status/', views.ShopProfileIsCompleteStatus.as_view(),
         name='shop_profile_complete_status'),

    # shop Panel
    path('shop-panel/', views.ShopPanelApiView.as_view(), name='shop_panel'),

    # shop type and monetary unit choices
    path('shop-choices/', views.ShopChoicesView.as_view(), name='shop_choices'),

    # delete profile fields by admin
    path('shop/reject-profile-fields/<uuid:shop_id>/', views.ClearProfileAttributeView.as_view(),
         name='reject_profile_fields'),

    # shop certificates, Admin, Weekly plan urls
    path('', include(router.urls)),

    # ID Card
    # path('user/id-card/', views.ShopIdCardFileApiView.as_view(), name='shop_owner_id_card'),

    # Working Days and Hours
    path('shop/weekly-plan/', views.ShopWeeklyPlanAPIView.as_view(), name='shop_weekly_plan'),
    path('shop/weekly-plan-hours/<int:pk>/', views.ShopOpenHoursDetailAPIView.as_view(), name='open_hours_detail'),

    # Media type Choices
    path('shop-media-type-choices/', views.ShopMediaTypeChoicesView.as_view(), name='shop_media_type_choices'),
    # # user profile
    # path('profile/', views.ShopProfileApiView.as_view(), name='user_profile'),
    #
    # # Cafe Menu
    # path('cafe-menu/<uuid:shop_id>/', views.CafeMenuApiView.as_view(), name='cafe_menu'),
    #
    # path('<uuid:shop_id>/', include(router.urls)),

    #     path('shops/<uuid:shop_id>/products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'})),
    #     path('shops/<uuid:shop_id>/products/<uuid:pk>/',
    #          ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]
