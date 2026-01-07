from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'

router = DefaultRouter()

router.register('brands', views.ProductBrandViewSet, basename='product_brand')
router.register('shop-products-categories', views.ShopProductCategoryViewSet, basename='shop_product_category')
router.register('cafe-products-categories', views.CafeProductCategoryViewSet, basename='cafe_product_category')

router.register('products', views.ProductViewSet, basename='product')

router.register(r'features', views.FeatureViewSet, basename='feature')

router.register(r'bundles', views.ProductBundleViewSet, basename='bundle')

# product File manager
router.register(r'product-media-files', views.ProductMediaFilesViewSet, basename='product_media_files')

urlpatterns = [
    # Active and Inactive the Product
    path('product/<uuid:pk>/toggle-active/', views.ToggleProductActiveView.as_view(), name='toggle_product_active'),

    # Price, Discount and ordering number change
    path('products/<uuid:pk>/update-pricing/', views.UpdateProductPricingView.as_view(), name='update_product_pricing'),

    # Product media type choices
    path('product-media-files-choices/', views.ProductMediaChoicesView.as_view(), name='product_media_files_choices'),

    # cafe product category choices
    path('cafe-products-categories-choices/', views.CafeCategoryChoicesView.as_view(),
         name='cafe_product_categories_choices'),

    # Shop product category choices
    path('shop-products-categories-choices/', views.ShopProductCategoryChoicesView.as_view(),
         name='shop_products_categories_choices'),

    # Product Choices
    path('products-types-choices/', views.ProductChoicesView.as_view(), name='products_types_choices'),

    path('', include(router.urls)),
]

# ==============================================================================================
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import (
#     ProductViewSet, ProductImageViewSet, ProductBrandViewSet, ShopProductCategoryViewSet, CafeProductCategoryViewSet,
#     FeatureViewSet, ProductBundleViewSet, ProductBundleItemViewSet
# )
#
# router = DefaultRouter()
# router.register('products', ProductViewSet, basename='product')
# router.register('product-images', ProductImageViewSet, basename='product-image')
# router.register('product-brands', ProductBrandViewSet, basename='product-brand')
# router.register('shop-product-categories', ShopProductCategoryViewSet, basename='shop-product-category')
# router.register('cafe-product-categories', CafeProductCategoryViewSet, basename='cafe-product-category')
# router.register('features', FeatureViewSet, basename='feature')
# router.register('product-bundles', ProductBundleViewSet, basename='product-bundle')
# router.register('product-bundle-items', ProductBundleItemViewSet, basename='product-bundle-item')
#
# urlpatterns = [
#     path('', include(router.urls)),
# ]

# =================================================================


# from rest_framework.routers import DefaultRouter
# from .views import (
#     ProductViewSet, FeatureViewSet, ProductFeatureViewSet,
#     ProductBundleViewSet, ProductBundleItemViewSet,
#     ProductBrandViewSet, ProductTypeViewSet,
#     ProductCategoryViewSet, ProductParentCategoryViewSet
# )
#
# app = 'api-v1'
#
# router = DefaultRouter()
# router.register(r'products', ProductViewSet, basename='product')
# router.register(r'features', FeatureViewSet, basename='feature')
# router.register(r'product-features', ProductFeatureViewSet, basename='product-feature')
# router.register(r'bundles', ProductBundleViewSet, basename='bundle')
# router.register(r'bundle-items', ProductBundleItemViewSet, basename='bundle-item')
# router.register(r'product-brands', ProductBrandViewSet, basename='product-brand')
# router.register(r'product-types', ProductTypeViewSet, basename='product-type')
# router.register(r'product-categories', ProductCategoryViewSet, basename='product-category')
# router.register(r'parent-categories', ProductParentCategoryViewSet, basename='parent-category')
#
# urlpatterns = router.urls
#
#
#
#
#
#
# # from django.urls import path, include
# # from . import views
# # from rest_framework.routers import DefaultRouter
# # from django.urls import path, include
# # from . import views
# # from rest_framework.routers import DefaultRouter
# #
# # app = 'api-v1'
# #
# # router = DefaultRouter()
# # router.register('product', views.ProductModelViewSet, basename='product')
# #
# # urlpatterns = [
# #
# #
# #     # path('product/<uuid:product_id>/', views.ProductDetail.as_view(), name='product_detail'),
# # ]
# # urlpatterns += router.urls
# #
# #
