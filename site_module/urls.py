from django.urls import path,include




urlpatterns = [
    path('api/v1/', include('site_module.api.v1.urls'))

]


