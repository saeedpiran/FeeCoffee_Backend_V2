from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response

from product_module.models import Product
from .pagination import ProductPagination
from .permissions import IsAdminOrSuperuserOrReadOnly
from .serializers import ProductSerializer, ShopBannerSerializer
from ...models import ShopMarketBanner


class ShopMarketIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__url_title']  # Example field, add more if needed
    search_fields = ['name']
    ordering_fields = ['created_date', 'last_price']

    def get_queryset(self):

        user = self.request.user
        is_wholesale = False
        if user.is_authenticated:
            is_wholesale = user.user_type == 'seller'  # Assuming user_type attribute

        # market_type = self.request.query_params.get('market_type', 'retail')
        # is_wholesale = True if market_type == 'wholesale' else False

        # Base filter
        base_filter = {
            'is_active': True,
            'is_delete': False,
            'is_wholesale': is_wholesale,
            'product_type': 'shop'
        }

        return Product.objects.filter(**base_filter).order_by('created_date')

    def list(self, request):
        queryset = self.get_queryset()

        # Apply filtering and ordering
        queryset = self.filter_queryset(queryset)

        # # Apply filtering
        # for backend in list(self.filter_backends):
        #     queryset = backend().filter_queryset(request, queryset, self)

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        # Serialize the data
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response({'products': serializer.data})

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class ShopBannerList(ListCreateAPIView):
    """getting a list of Cafe Banners and creating an article"""
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    serializer_class = ShopBannerSerializer
    queryset = ShopMarketBanner.objects.filter(is_active=True)


class ShopBannerDetail(DestroyAPIView):
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    serializer_class = ShopBannerSerializer
    queryset = ShopMarketBanner.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "بنر مورد نطر با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT)
