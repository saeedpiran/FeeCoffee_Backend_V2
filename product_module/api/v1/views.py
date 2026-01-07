from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from product_module.api.v1.permissions import IsAdminOrSuperuserOrReadOnly, IsShopOwnerOrAdmin
from product_module.api.v1.serializers import ProductBrandSerializer, ShopProductsCategorySerializer, \
    CafeProductsCategorySerializer, \
    EmptyRestoreSerializer, ProductSerializer, FeatureSerializer, ProductBundleSerializer, ProductMediaFilesSerializer, \
    ProductToggleActiveSerializer, ProductPricingUpdateSerializer
from product_module.models import ProductBrand, ShopProductCategory, CafeProductCategory, Product, Feature, \
    ProductBundle, ProductMediaFiles
from shop_module.models import Shop


# ------------------------------------------------------------
# product brands
class ProductBrandViewSet(viewsets.ModelViewSet):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]  # Define custom permission

    def get_permissions(self):
        # Grant permissions based on HTTP methods
        if self.action in ['update', 'partial_update', 'destroy']:  # Edit or delete
            self.permission_classes = [IsAdminOrSuperuserOrReadOnly]  # Only admins can edit/delete
        elif self.action == 'create':  # Create brand
            self.permission_classes = [IsAuthenticated]
        else:  # Read operations
            self.permission_classes = [IsAdminOrSuperuserOrReadOnly]  # Admin can do all, others read-only
        return [permission() for permission in self.permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "برندها با موفقیت فراخوانی شدند."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "برند با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "status": True,
                    "data": serializer.data,  # Optionally include the created brand's details
                    "message": "برند با موفقیت ایجاد شد.",
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response(
            {
                "status": False,
                "error": "برند مورد نظر ثبت نشد.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST, )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "برند با موفقیت به‌روز رسانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "data": {},
            "message": "برند با موفقیت حذف شد."
        }, status=status.HTTP_200_OK)


# -------------------------------------------------------------------------
# Shop products categories
class ShopProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ShopProductsCategorySerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    queryset = ShopProductCategory.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent_category']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                "success": True,
                "data": serializer.data,
                "message": "دسته بندی های محصولات فروشگاه با موفقیت فراخوانی شد."
            }
            return self.get_paginated_response(response_data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی های محصولات فروشگاه با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی های محصولات فروشگاه با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی های محصولات فروشگاه با موفقیت ایجاد شد."
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی های محصولات فروشگاه با موفقیت بروز رسانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "data": {},
            "message": "دسته بندی های محصولات فروشگاه با موفقیت حذف شد."
        }, status=status.HTTP_200_OK)


# Shop product category choices
class ShopProductCategoryChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        parent_category_choices = [
            {"value": key, "label": label}
            for key, label in ShopProductCategory.PARENT_CATEGORY_CHOICES
        ]
        Response.message = "مقادیر انتخاب فراخوانی شدند."
        return Response({
            "parent_category_choices": parent_category_choices
        })


# class ShopProductCategoryViewSet(viewsets.ModelViewSet):
#     serializer_class = ShopProductsCategorySerializer
#     permission_classes = [IsAdminOrSuperuserOrReadOnly]
#     queryset = ShopProductCategory.objects.all()
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['parent_category']
#
#     # def get_queryset(self):
#     #         queryset = ShopProductCategory.objects.all()
#     #         parent_category_id = self.request.query_params.get('parent_category', None)
#     #         if parent_category_id:
#     #             queryset = queryset.filter(parent_category__id=parent_category_id)
#     #         return queryset


# -------------------------------------------------------------------------
# Cafe products categories
class CafeProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CafeProductsCategorySerializer
    permission_classes = [IsShopOwnerOrAdmin]

    def get_queryset(self):
        """
        Return a queryset filtered by the user's associated shop,
        or all items for a superuser. Also returns an empty queryset when
        being accessed during schema generation for Swagger.
        """
        # Bypass user-specific logic during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return CafeProductCategory.objects.none()

        user = self.request.user

        if user.is_superuser:
            # Superusers see all categories
            qs = CafeProductCategory.objects.all()
        else:
            try:
                shop = self.request.user.shopprofile.shop
            except (AttributeError, self.request.user.shopprofile.RelatedObjectDoesNotExist):
                raise ValidationError("کاربر شما به یک فروشگاه متصل نیست.")
            qs = CafeProductCategory.objects.filter(shop=shop)

        # Filter based on deletion status
        if self.action == 'list_deleted':
            qs = qs.filter(is_deleted=True)
        else:
            qs = qs.filter(is_deleted=False)

        # Annotate with the count of related products and order the queryset
        qs = qs.annotate(
            products_count=Count('products', filter=Q(products__is_deleted=False))
        ).order_by('-created_date')
        return qs

        # """
        # Depending on the action, return either non-deleted or deleted items.
        # For the 'list_deleted' action, return only soft-deleted items.
        # Filter categories by shop based on the requesting user's shop.
        # """
        # try:
        #     shop = self.request.user.shopprofile.shop
        # except AttributeError:
        #     raise ValidationError("کاربر شما به یک فروشگاه متصل نیست.")
        #
        # # if self.action == 'list_deleted':
        # #     return CafeProductCategory.objects.filter(is_deleted=True, shop=shop)
        # # return CafeProductCategory.objects.filter(is_deleted=False, shop=shop)
        #
        # if self.action == 'list_deleted':
        #     qs = CafeProductCategory.objects.filter(is_deleted=True, shop=shop)
        # else:
        #     qs = CafeProductCategory.objects.filter(is_deleted=False, shop=shop)
        #
        #     # Annotate with the count of related products
        #     # Note: 'products' is the related_name on the cafe_category field in Product.
        # qs = qs.annotate(products_count=Count('products'))
        #
        # # Order by created_date (use '-created_date' for descending or 'created_date' for ascending)
        # qs = qs.order_by('-created_date')
        #
        # return qs

    def get_object(self):
        """
        Override object retrieval to allow access to soft-deleted objects
        when performing a restore.
        """
        if self.action == 'restore':
            queryset = CafeProductCategory.objects.all()
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(queryset, **filter_kwargs)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def perform_create(self, serializer):
        """
        On creation, automatically assign the shop for non-superusers.
        Superusers are allowed to create a category without auto-assigning a shop.
        """
        # Automatically assign the `shop` based on the authenticated user's `ShopProfile`.
        user = self.request.user
        if user.is_superuser:
            # Superusers may supply the shop manually or the serializer
            serializer.save()
        else:
            try:
                shop = user.shopprofile.shop
            except (AttributeError, user.shopprofile.RelatedObjectDoesNotExist):
                raise ValidationError("کاربر شما به یک فروشگاه متصل نیست.")
            serializer.save(shop=shop)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        response_data = {
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی محصول کافه با موفقیت ایجاد شد."  # Custom success message
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        """
        Override list() to wrap the list response in the custom envelope.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page is not None else self.get_serializer(queryset,
                                                                                                       many=True)
        response_data = {
            "success": True,
            "data": serializer.data,
            "message": "دسته بندی های محصول کافه با موفقیت فراخوانی شدند."
        }
        if page is not None:
            return self.get_paginated_response(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a category and return it in the envelope structure.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "آیتم با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete the category by marking it as deleted and unverified.
        """
        instance = self.get_object()
        if instance.is_deleted:
            return Response({
                "success": False,
                "error": "آیتم قبلاً حذف شده است."
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.is_deleted = True
        instance.is_verified = False
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "آیتم با موفقیت حذف شد.",
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=EmptyRestoreSerializer())
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted category.
        """
        instance = self.get_object()
        if not instance.is_deleted:
            return Response({
                "success": False,
                "error": "آیتم قبلاً بازیابی شده است یا حذف نشده است."
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.is_deleted = False
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "آیتم با موفقیت بازیابی شد.",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='deleted')
    def list_deleted(self, request):
        """
        Custom endpoint to list all soft-deleted categories.
        """
        deleted_items = self.get_queryset()  # Already filtered via get_queryset
        serializer = self.get_serializer(deleted_items, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "لیست آیتم‌های حذف شده.",
        }, status=status.HTTP_200_OK)

# cafe product category choices
class CafeCategoryChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        parent_category_choices = [
            {"value": value, "label": label}
            for value, label in CafeProductCategory.CAFE_MENU_CATEGORY_TYPE_CHOICES
        ]
        Response.message = "مقادیر انتخاب فراخوانی شدند."
        return Response({
            "parent_category_choices": parent_category_choices
        })
# ------------------------------------------------------------------------
# Product
# Product viewset with role‑based filtering, soft deletion, and recovery.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsShopOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter]
    # No ordering fields allowed from the request
    ordering_fields = ['created_date', 'price', 'name']  # allow clients to order by these fields
    ordering = ['-created_date']  # default ordering

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()

        user = self.request.user
        if user.is_superuser:
            return Product.all_objects.all()
        else:
            return Product.objects.filter(shop__profile__owner=user)

    def list(self, request, *args, **kwargs):
        # Apply all backend filters including ordering
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        response_data = {
            "success": True,
            "data": serializer.data,
            "message": "محصولات با موفقیت فراخوانی شدند."
        }
        if page is not None:
            return self.get_paginated_response(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "محصول با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "محصول با موفقیت ایجاد شد."
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not request.user.is_superuser and instance.shop.profile.owner != request.user:
            return Response({
                "success": False,
                "data": {},
                "errors": "شما برای انجام تغییرات مجوز ندارید."
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "محصول با موفقیت به‌روز رسانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_verified = False
        instance.save()
        return Response({
            "success": True,
            "data": {},
            "message": "محصول با موفقیت حذف شد."
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='deleted')
    def deleted(self, request):
        user = request.user
        if user.is_superuser:
            queryset = Product.all_objects.filter(is_deleted=True)
        else:
            queryset = Product.all_objects.filter(shop__profile__owner=user, is_deleted=True)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        response_data = {
            "success": True,
            "data": serializer.data,
            "message": "محصولات حذف شده با موفقیت فراخوانی شدند."
        }
        if page is not None:
            return self.get_paginated_response(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='recover')
    def recover(self, request, pk=None):
        instance = get_object_or_404(Product.all_objects, pk=pk)
        instance.is_deleted = False
        instance.is_verified = False  # Reset verification status upon recovery.
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "محصول با موفقیت بازیابی شد."
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            shop_id = self.request.data.get('shop')
            shop = get_object_or_404(Shop, id=shop_id)
        else:
            shop = get_object_or_404(Shop, profile__owner=user)
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        # Anytime a user updates the product, is_verified is reset to False.
        serializer.save(is_verified=False)


# product choices
class ProductChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        product_type_choices = [
            {"value": key, "label": label}
            for key, label in Product.PRODUCT_TYPE_CHOICES
        ]
        Response.message = "مقادیر انتخاب فراخوانی شدند."
        return Response({"product_type_choices": product_type_choices})

# ----------------------------------------------------------------------
# Bundle
class ProductBundleViewSet(ModelViewSet):
    queryset = ProductBundle.objects.all()
    serializer_class = ProductBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # When generating the schema (via drf-yasg), return an empty queryset.
        if getattr(self, 'swagger_fake_view', False):
            return ProductBundle.objects.none()

        user = self.request.user
        # If user isn’t authenticated, return an empty queryset.
        if not user or not user.is_authenticated:
            return ProductBundle.objects.none()

        # Superusers can see all bundles; shop owners only see bundles for shops they own.
        if user.is_superuser:
            return ProductBundle.objects.all()
        else:
            return ProductBundle.objects.filter(shop__profile__owner=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "باندل کالاها با موفقیت فراخوانی شدند."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "باندل کالا با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # If validation fails, your custom exception handler wraps the error response.
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "باندل کالا با موفقیت ایجاد شد."
        }, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        shop_id = self.request.data.get('shop')
        # For non-superusers, ensure the shop belongs to the current user.
        if not user.is_superuser:
            shop = get_object_or_404(Shop, id=shop_id, profile__owner=user)
        else:
            shop = get_object_or_404(Shop, id=shop_id)
        serializer.save(shop=shop)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Verify ownership for non‑admin users.
        if not request.user.is_superuser and instance.shop.profile.owner != request.user:
            return Response({
                "success": False,
                "data": {},
                "errors": "شما برای انجام تغییرات مجوز ندارید."
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "باندل کالا با موفقیت به‌روز رسانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Verify ownership for non‑admin users.
        if not request.user.is_superuser and instance.shop.profile.owner != request.user:
            return Response({
                "success": False,
                "data": {},
                "errors": "شما برای انجام تغییرات مجوز ندارید."
            }, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({
            "success": True,
            "data": {},
            "message": "باندل کالا با موفقیت حذف شد."
        }, status=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------------------------
# Admin
# Featutes
class FeatureViewSet(ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "ویژگی‌ها با موفقیت دریافت شدند."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "ویژگی با موفقیت دریافت شد."
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # Raises exception if invalid; your custom exception handler will format the error.
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "ویژگی با موفقیت ایجاد شد."
        }, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "ویژگی با موفقیت به‌روز رسانی شد."
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "data": {},
            "message": "ویژگی با موفقیت حذف شد."
        }, status=status.HTTP_204_NO_CONTENT)


# class FeatureViewSet(ModelViewSet):
#     queryset = Feature.objects.all()
#     serializer_class = FeatureSerializer
#     permission_classes = [IsAdminOrSuperuserOrReadOnly]  # Change this if you want different permissions

# Optionally, you can override get_queryset() if you want to filter based on the request user.
# For example, if shop owners can view their shop’s features, you might do:
#
# def get_queryset(self):
#     user = self.request.user
#     if user.is_superuser:
#         return Feature.objects.all()
#     # If shop owners should only see features relevant to their shop,
#     # you might filter those based on some criteria. Otherwise, just return all features.
#     return Feature.objects.all()

# --------------------------------------------------------------
# Active and Inactive the Product
class ToggleProductActiveView(APIView):
    """
    API endpoint that toggles the 'is_active' status of a Product.
    If the product is active (True), it becomes inactive (False), and vice versa.
    """
    permission_classes = [IsShopOwnerOrAdmin]

    def post(self, request, pk, format=None):
        product = get_object_or_404(Product, pk=pk)
        product.is_active = not product.is_active  # Toggle the is_active state.
        # product.is_verified = False
        product.save()
        serializer = ProductToggleActiveSerializer(product)
        Response.message = "مقدار فعال/غیرفعال با موفقیت تغییر یافت."
        return Response(serializer.data, status=status.HTTP_200_OK)

# -----------------------------------------------------------------
# Price, Discount and ordering number change
class UpdateProductPricingView(APIView):
    """
    API endpoint to update the price, discount, and ordering number for a Product.

    You can update one, two, or all three fields by sending a PATCH request.

    **Example Request URLs:**
    - PATCH /products/<uuid:pk>/update-pricing/

    **Example Request Body:**
    {
        "price": 150,
        "discount": 20,
        "ordering_number": 5
    }
    """

    permission_classes = [IsShopOwnerOrAdmin]

    @swagger_auto_schema(
        request_body=ProductPricingUpdateSerializer,
        responses={200: ProductPricingUpdateSerializer()}
    )

    def patch(self, request, pk, format=None):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductPricingUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            Response.message = "مقادیر مورد نظر با موفقیت تغییر یافت."
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------
# File manager
class ProductMediaFilesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows shop media files to be viewed, uploaded, edited and deleted.
    For list, create, retrieve, and update:
      - The shop owner (as determined by the shop profile owner) has access.
    For destroy (delete):
      - Only a superuser or staff is allowed.
    """
    serializer_class = ProductMediaFilesSerializer
    parser_classes = [MultiPartParser, FormParser]
    # NOTE: pagination_class is set globally in settings or omitted here since grouping is used.
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['media_type', 'media_category', 'is_global']
    search_fields = ['media_type', 'media_category']

    def get_queryset(self):
        # Short-circuit during schema generation or if the user isn't authenticated
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return ProductMediaFiles.objects.none()

        # For staff or superusers, return all files.
        if self.request.user.is_staff or self.request.user.is_superuser:
            query = ProductMediaFiles.objects.all()
        else:
            # For normal shop owners, return files that match their shop or are global.
            query = ProductMediaFiles.objects.filter(
                Q(shop__profile__owner=self.request.user.id) | Q(is_global=True)
            )

        # Order the files by created_date in ascending order.
        return query.order_by('-created_date')

        # # For staff or superusers, return all files.
        # if self.request.user.is_staff or self.request.user.is_superuser:
        #     return ProductMediaFiles.objects.all()
        #
        # # For normal shop owners,
        # # use self.request.user.id to ensure a valid UUID/identifier is used.
        # return ProductMediaFiles.objects.filter(
        #     Q(shop__profile__owner=self.request.user.id) | Q(is_global=True)
        # )

    def get_permissions(self):
        if self.action == "destroy":
            # For deletion, only admin or staff are allowed.
            permission_classes = [permissions.IsAdminUser]
        else:
            # For all other actions, enforce shop ownership or admin rights.
            permission_classes = [IsShopOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def _group_by_media_type(self, serialized_files):
        """
        Helper function that groups file objects by media_type.
        Returns a dictionary with the media_type as keys and lists of file data as values.
        """
        grouped = {}
        for file in serialized_files:
            media_type = file.get("media_type")
            if media_type not in grouped:
                grouped[media_type] = []
            grouped[media_type].append(file)
        return grouped

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search query for filtering by media_type (partial match)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'media_type',
                openapi.IN_QUERY,
                description='Filter files by media_type (exact match)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'media_category',
                openapi.IN_QUERY,
                description='Filter files by media_category (exact match)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_global',
                openapi.IN_QUERY,
                description='Filter files by global flag (true/false)',
                type=openapi.TYPE_BOOLEAN
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List files grouped into global and shop files.
        No pagination is applied; all matching records are loaded.
        """
        # Apply filtering / search.
        queryset = self.filter_queryset(self.get_queryset())

        # Split the resulting queryset into two groups.
        global_files_qs = queryset.filter(is_global=True)
        local_files_qs = queryset.exclude(is_global=True)

        # Serialize both groups.
        global_serialized = self.get_serializer(global_files_qs, many=True).data
        shop_serialized = self.get_serializer(local_files_qs, many=True).data

        # Group them by media_type.
        grouped_global_files = self._group_by_media_type(global_serialized)
        grouped_local_files = self._group_by_media_type(shop_serialized)

        response_data = {
            "global_files": grouped_global_files,
            "local_files": grouped_local_files
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.message = "فایلها با موفقیت فراخوانی شدند."
        return response

        # return Response({
        #     "success": True,
        #     "data": response_data,
        #     "message": "فایلها با موفقیت فراخوانی شد."
        # }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Override create() to return the created file in the response envelope.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.message = "فایل با موفقیت ایجاد شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "فایل با موفقیت ایجاد شد."
        # }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve() to return a file record in the envelope.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.message = "فایل با موفقیت فراخوانی شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "فایل با موفقیت فراخوانی شد."
        # }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Override update() to update a file record and return the envelope.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.message = "فایل با موفقیت بروز رسانی شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": serializer.data,
        #     "message": "فایل با موفقیت بروز رسانی شد."
        # }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy() to delete a file record and return the success envelope.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        response = Response({}, status=status.HTTP_204_NO_CONTENT)
        response.message = "فایل با موفقیت حذف شد."
        return response

        # return Response({
        #     "success": True,
        #     "data": {},
        #     "message": "فایل با موفقیت حذف شد."
        # }, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        """
        Assign shop and is_global fields based on the authenticated user.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # For admin uploads, assign shop=None and ensure the file is global.
            serializer.save(shop=None, is_global=True)
        else:
            try:
                shop = Shop.objects.get(profile__owner=user)
            except Shop.DoesNotExist:
                raise ValidationError({
                    "shop": "فروشگاهی برای کاربر جاری ثبت نشده است."
                })
            serializer.save(shop=shop, is_global=False)

# Product media type choices
class ProductMediaChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        media_type_choices = [
            {"value": key, "label": label}
            for key, label in ProductMediaFiles.MEDIA_TYPE_CHOICES
        ]
        media_category_choices = [
            {"value": key, "label": label}
            for key, label in ProductMediaFiles.MEDIA_CATEGORY_CHOICES
        ]
        Response.message = "مقادیر انتخاب فراخوانی شدند."
        return Response({
            "media_type_choices": media_type_choices,
            "media_category_choices": media_category_choices
        })

