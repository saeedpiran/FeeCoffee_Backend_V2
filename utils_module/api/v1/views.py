import requests
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Search the locations with search bar
class NeshanSearchAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('term', openapi.IN_QUERY, description="Search Term", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        api_key = 'service.375767c29a45472eb62ca4dbaa108882'

        term = request.GET.get('term')
        # lat = request.GET.get('lat')
        # long = request.GET.get('lng')

        # term = 'تهران'
        lat = 35.699756
        long = 51.338076

        url = f'https://api.neshan.org/v1/search?term={term}&lat={lat}&lng={long}'
        headers = {'Api-Key': api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=response.status_code)


# Get address by the lat and long
class NeshanReverseGeocodingAPIView(APIView):
    @staticmethod
    def get_location_data(lat, long):
        api_key = 'service.ae1bf0d288834331a00f2b92d2378621'
        url = f'https://api.neshan.org/v2/reverse?lat={lat}&lng={long}'
        headers = {'Api-Key': api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            state = data.get('state', '')
            city = data.get('city', '')
            addresses = data.get('addresses', [])
            detailed_address = addresses[0].get('formatted', '') if addresses else ''

            return data, state, city, detailed_address, status.HTTP_200_OK
        else:
            return None, None, None, response.status_code

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude", type=openapi.TYPE_NUMBER),
            openapi.Parameter('long', openapi.IN_QUERY, description="Longitude", type=openapi.TYPE_NUMBER)
        ]
    )
    def get(self, request):
        lat = request.GET.get('lat')
        long = request.GET.get('long')

        # request.session['latitude'] = 35.659756
        # request.session['longitude'] = 51.338076
        #
        # lat = request.session.get('latitude', 0)
        # long = request.session.get('longitude', 0)

        if not lat or not long:
            return Response({
                'status': False,
                'error': 'Latitude and longitude are required parameters.'},
                status=status.HTTP_400_BAD_REQUEST)

        data, state, city, detailed_address, status_code = self.get_location_data(lat, long)
        data = {
            'data': data,
            'state': state,
            'city': city,
            'address': detailed_address
        }

        return Response(data, status=status_code)

# class NeshanReverseGeocodingAPIView(APIView):
#     def get(self, request):
#         api_key = 'service.ae1bf0d288834331a00f2b92d2378621'
#
#         # lat = request.GET.get('lat')
#         # long = request.GET.get('lng')
#
#         request.session['latitude'] = 35.659756
#         request.session['longitude'] = 51.338076
#
#         lat = request.session.get('latitude', 0)
#         long = request.session.get('longitude', 0)
#
#         url = f'https://api.neshan.org/v2/reverse?lat={lat}&lng={long}'
#         headers = {'Api-Key': api_key}
#         response = requests.get(url, headers=headers)
#
#         if response.status_code == 200:
#             return Response(response.json(), status=status.HTTP_200_OK)
#         else:
#             return Response(response.json(), status=response.status_code)
