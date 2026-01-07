from django.urls import path

from home_module import views

urlpatterns = [
    path('', views.home_index, name='home_page'),
    path('transfer/', views.transfer_page_shop, name='transfer_shop_page'),
]