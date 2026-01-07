# urls.py
from django.urls import path

from .views import NeshanSearchAPIView, NeshanReverseGeocodingAPIView

app = 'api-v1'

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Neshan API",
#         default_version='v1',
#         description="Neshan Reverse Geocoding API",
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    # search locations by search bar from neshan
    path('neshan-search/', NeshanSearchAPIView.as_view(), name='neshan_search'),

    # Get Address from lat ang long from neshan
    path('neshan-reverse-geocoding/', NeshanReverseGeocodingAPIView.as_view(), name='neshan_reverse_geocoding'),
]
