from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework import mixins, viewsets
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response

from shop_module.models import Shop
from .pagination import DefaultPagination
from .permissions import IsAdminOrSuperuserOrReadOnly
from .serializers import CafeSerializer, CafeBannerSerializer
from ...models import CafeMarketBanner


# class CafeMarketIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     serializer_class = CafeSerializer
#     pagination_class = DefaultPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['pickup', 'free_delivery', 'products__is_special', 'bundles__is_active']
#     search_fields = ['name']
#     ordering_fields = ['distance']
#
#     def get_queryset(self):
#         request = self.request
#
#         # # Get latitude and longitude from session
#         latitude = request.data.get('latitude', 0)
#         longitude = request.data.get('longitude', 0)
#
#         # Get latitude and longitude from the request data
#         # marker_position = json.loads(request.body).get('markerPosition', [0, 0])
#         # latitude, longitude = marker_position
#
#         print(latitude)
#         print(longitude)
#
#         # Base queryset
#         queryset = Shop.objects.filter(
#             is_active=True,
#             products__is_active=True,
#             shop_type__in=['cafe', 'both']
#         ).distinct()
#
#         # Annotate queryset with distance
#         queryset = queryset.annotate(
#             distance=ExpressionWrapper(
#                 6371 * ACos(
#                     Cos(Radians(latitude)) * Cos(Radians(F('latitude'))) *
#                     Cos(Radians(F('longitude')) - Radians(longitude)) +
#                     Sin(Radians(latitude)) * Sin(Radians(F('latitude')))
#                 ),
#                 output_field=FloatField()
#             )
#         )
#
#         # Order the queryset by distance
#         queryset = queryset.order_by('distance')
#
#         return queryset
#
#     def list(self, request, *args, **kwargs):
#         # Get latitude and longitude from session
#         latitude = request.session.get('latitude', 0)
#         longitude = request.session.get('longitude', 0)
#
#         # Filter the queryset
#         queryset = self.filter_queryset(self.get_queryset())
#
#         # # Calculate distances and sort cafes
#         # nearby_cafes = []
#         # for cafe in queryset:
#         #     if cafe.latitude and cafe.longitude:
#         #         distance = cafe.distance
#         #         cafe.distance = distance
#         #         nearby_cafes.append(cafe)
#
#         # nearby_cafes.sort(key=lambda x: x.distance)
#
#         # Paginate the results
#         paginator = DefaultPagination()
#         page = paginator.paginate_queryset(queryset, request)
#         if page is not None:
#             serializer = CafeSerializer(page, many=True, context={'request': request})
#             return paginator.get_paginated_response(serializer.data)
#
#         serializer = CafeSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#
#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset


# from rest_framework import mixins, viewsets
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters, status
# from rest_framework.response import Response
# from django.db.models import F, FloatField, ExpressionWrapper
# from django.db.models.functions import ACos, Cos, Radians, Sin
#
# class CafeMarketIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     serializer_class = CafeSerializer
#     pagination_class = DefaultPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['pickup', 'free_delivery', 'products__is_special', 'bundles__is_active']
#     search_fields = ['name']
#     ordering_fields = ['distance']
#
#     def get_queryset(self):
#         request = self.request
#
#         latitude = float(request.query_params.get('lat', 0))
#         longitude = float(request.query_params.get('long', 0))
#
#         queryset = Shop.objects.filter(
#             is_active=True,
#             products__is_active=True,
#             shop_type__in=['cafe', 'both']
#         ).distinct()
#
#         queryset = queryset.annotate(
#             distance=ExpressionWrapper(
#                 6371 * ACos(
#                     Cos(Radians(latitude)) * Cos(Radians(F('latitude'))) *
#                     Cos(Radians(F('longitude')) - Radians(longitude)) +
#                     Sin(Radians(latitude)) * Sin(Radians(F('latitude')))
#                 ),
#                 output_field=FloatField()
#             )
#         )
#
#         queryset = queryset.order_by('distance')
#
#         return queryset
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(queryset, request)
#         if page is not None:
#             serializer = self.serializer_class(page, many=True, context={'request': request})
#             return paginator.get_paginated_response(serializer.data)
#
#         serializer = self.serializer_class(queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#
#     # def create(self, request, *args, **kwargs):
#     #     serializer = self.serializer_class(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset


class CafeMarketIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CafeSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pickup', 'free_delivery', 'products__is_special', 'bundles__is_active']
    search_fields = ['name']
    ordering_fields = ['distance']

    latitude_param = openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude", type=openapi.TYPE_NUMBER)
    longitude_param = openapi.Parameter('long', openapi.IN_QUERY, description="Longitude", type=openapi.TYPE_NUMBER)

    @swagger_auto_schema(manual_parameters=[latitude_param, longitude_param])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context={'request': request})
            # print(serializer.data)  # Print the entire serialized output
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def get_queryset(self):
        request = self.request

        latitude = float(request.query_params.get('lat', 0))
        longitude = float(request.query_params.get('long', 0))
        
        # Use prefetch_related for products and bundles to reduce query overhead
        queryset = Shop.objects.prefetch_related('products', 'bundles').filter(
            # is_verified=True,
            products__is_active=True,
            shop_type__in=['cafe', 'both']
        ).distinct()

        queryset = queryset.annotate(
            distance=ExpressionWrapper(
                6371 * ACos(
                    Cos(Radians(latitude)) * Cos(Radians(F('profile__latitude'))) *
                    Cos(Radians(F('profile__longitude')) - Radians(longitude)) +
                    Sin(Radians(latitude)) * Sin(Radians(F('profile__latitude')))
                ),
                output_field=FloatField()
            )
        ).filter(distance__lte=10000)  # Filter cafes within 15 km distance
        # print(queryset.annotate())
        queryset = queryset.order_by('distance')
        # print(queryset.query)

        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class CafeBannerList(ListCreateAPIView):
    """getting a list of Cafe Banners and creating an article"""
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    serializer_class = CafeBannerSerializer
    queryset = CafeMarketBanner.objects.filter(is_active=True)


class CafeBannerDetail(DestroyAPIView):
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    serializer_class = CafeBannerSerializer
    queryset = CafeMarketBanner.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "بنر مورد نطر با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT)
