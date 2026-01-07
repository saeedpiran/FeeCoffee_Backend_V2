from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app = 'api-v1'
#
# router = DefaultRouter()
# router.register(r'collection-categories', views.ImageCollectionCategoryViewSet,
#                 basename='image_collection_category')
# router.register(r'images', views.ImageCollectionImageViewSet,
#                 basename='image_collection_image')
#
# # router.register('article',views.ArticleModelViewSet,basename='article')
# # router.register('article_category',views.ArticleCategoryModelViewSet,basename='article_category')
# #
#
#
urlpatterns = [
    # path('images/category/<int:category_id>/', views.ImagesByCategoryListView.as_view(), name='images_by_category'),
]
# urlpatterns += router.urls
