from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('media_collection_module.api.v1.urls')),
]
