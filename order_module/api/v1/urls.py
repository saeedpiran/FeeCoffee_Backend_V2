from rest_framework.routers import DefaultRouter

app = 'api-v1'

router = DefaultRouter()

# router.register(r'orders', views.OrderViewSet, basename='order')
# router.register(r'order-details', views.OrderDetailViewSet, basename='order_detail')

urlpatterns = [
    # path('article-list/', views.article_list_view, name='articles_list'),
    # path('article-detail/<int:id>/', views.article_detail_view, name='articles_detail'),

    # path('article-list/', views.ArticleList.as_view(), name='articles_list'),
    # path('article-detail/<int:id>/', views.ArticleDetail.as_view(), name='articles_detail'),

    # path('article-list/', views.ArticleViewSet.as_view({'get':'list','post':'create'}),name='article_list'),
    # path('article-detail/<int:id>/', views.ArticleViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}),name='article_detail'),
]
urlpatterns += router.urls
