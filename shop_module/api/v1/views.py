# from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status, permissions
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied

from .serializers import ShopWeeklyPlanSerializer, ShopOpenHoursSerializer, \
    ClearProfileAttributeSerializer, ShopMediaFilesSerializer, \
    ShopProfileIsCompleteStatusSerializer, ShopProfileReadSerializer, ShopProfileWriteSerializer, \
    ShopPanelReadSerializer, ShopPanelWriteSerializer
from shop_module.models import Shop, ShopOpenHours, ShopMediaFiles
from shop_module.models import ShopProfile  # adjust imports as necessary
from .permissions import IsShopOwnerOrAdmin


# -----------------------------------------------------------


# Shop Profile
#  Profile API View with Dynamic Serializer Selection
class ShopProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsShopOwnerOrAdmin]

    def get_serializer_class(self):
        # Use the read serializer for GET, and the write serializer for updates.
        if self.request.method == 'GET':
            return ShopProfileReadSerializer
        return ShopProfileWriteSerializer

    def get_object(self):
        return get_object_or_404(ShopProfile, owner=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "اطلاعات پروفایل با موفقیت فراخوانی شد."
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Re-serialize using the read serializer for full details.
        read_serializer = ShopProfileReadSerializer(instance, context={'request': request})
        return Response({
            "success": True,
            "data": read_serializer.data,
            "message": "پروفایل با موفقیت بروز رسانی شد."
        }, status=status.HTTP_200_OK)

# ------------------------------------------------------
#   Signal to Update the Profile Completeness Flag
# ------------------------------------------------------
@receiver(post_save, sender=ShopProfile)
def complete_profile(sender, instance, **kwargs):
    required_fields = [
        instance.latitude,
        instance.longitude,
        instance.postal_code,
        instance.number,
        instance.address.strip() if instance.address else None,
        instance.city,
        instance.state,
        instance.owner.first_name.strip() if instance.owner.first_name else None,
        instance.owner.last_name.strip() if instance.owner.last_name else None,
        instance.owner.id_number
    ]

    # Validate completeness
    is_complete = all(field for field in required_fields)
    # print(is_complete)

    # Only update if there's a change
    if instance.is_complete != is_complete:
        # print(f"Updating is_complete for ShopProfile ID {instance.id} from {instance.is_complete} to {is_complete}")
        ShopProfile.objects.filter(pk=instance.pk).update(is_complete=is_complete)
        # This prevents triggering `post_save` again by avoiding a full `save()`

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Shop is complete Profile Status
class ShopProfileIsCompleteStatus(generics.RetrieveAPIView):
    """
    This endpoint returns:
      {"is_complete": <bool>, "user_type": "<user_type>", "message": "<message>"}

    The shop is retrieved via its `profile__owner` relation.
    """
    serializer_class = ShopProfileIsCompleteStatusSerializer
    permission_classes = [IsShopOwnerOrAdmin]

    def get_object(self):
        # Retrieve the shop using the correct relationship field.
        return get_object_or_404(Shop, profile__owner=self.request.user)

    def get(self, request, *args, **kwargs):
        shop = self.get_object()
        profile = shop.profile  # Assumes that Shop has a related profile.
        user_type = request.user.user_type

        if not profile.is_complete:
            response_data = {
                "success": False,
                "is_complete": profile.is_complete,
                "user_type": user_type,
                "message": "ابتدا باید پروفایل خود را تکمیل و تأیید کنید."
            }
        else:
            response_data = {
                "success": True,
                "is_complete": profile.is_complete,
                "user_type": user_type,
                "message": "پروفایل فروشگاه کامل است."
            }

        return Response(response_data, status=status.HTTP_200_OK)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Shop Panel
class ShopPanelApiView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving (GET) and updating (PUT/PATCH)
    the shop panel details associated with the logged-in shop owner.
    All shop and profile data is editable, while media files are provided via their IDs.
    """
    permission_classes = [IsShopOwnerOrAdmin]

    def get_queryset(self):
        return Shop.objects.select_related(
            'profile', 'profile__owner', 'logo'
        ).prefetch_related('banner').filter(profile__owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ShopPanelReadSerializer
        return ShopPanelWriteSerializer

    def get_object(self):
        queryset = self.get_queryset()
        try:
            shop_obj = queryset.get(profile__owner=self.request.user)
        except Shop.DoesNotExist:
            raise Http404("Record not found. (You do not have a shop.)")

        if not shop_obj.profile.is_complete:
            # Unconventional 200 OK response when profile is incomplete.
            return Response({
                "success": False,
                "is_completed": False,
                "message": "ابتدا باید پروفایل خود را تکمیل کنید."  # "Please complete your profile first."
            }, status=status.HTTP_200_OK)
        return shop_obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        shop_or_response = self.get_object()
        if isinstance(shop_or_response, Response):
            return shop_or_response
        serializer = self.get_serializer(shop_or_response)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "Shop panel retrieved successfully."
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        shop_or_response = self.get_object()
        if isinstance(shop_or_response, Response):
            return shop_or_response
        serializer = self.get_serializer(shop_or_response, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "Shop updated successfully."
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": serializer.errors,
            "message": "Invalid data. Please review the errors."
        }, status=status.HTTP_400_BAD_REQUEST)

# class ShopPanelApiView(generics.RetrieveUpdateAPIView):
#     """
#     API endpoint for retrieving (GET) and updating (PUT/PATCH)
#     the shop profile associated with the logged-in user.
#     Excludes certificate and ID card fields.
#     """
#     permission_classes = [IsShopOwnerOrAdmin]
#     serializer_class = ShopPanelSerializer
#
#     def get_queryset(self):
#         # Filter queryset by the owner for efficiency
#         return Shop.objects.select_related(
#             'profile', 'profile__owner', 'logo'
#         ).prefetch_related(
#             'banner'
#         ).filter(profile__owner=self.request.user)
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         try:
#              # Attempt to get the single shop for the authenticated user
#              obj = queryset.get(profile__owner=self.request.user)
#         except Shop.DoesNotExist:
#              # --- Handle case where user has no shop with a 404 ---
#              raise Http404("رکورد مورد نظر یافت نشد. (شما فروشگاهی ندارید)") # Provide a specific message
#
#         # Check permissions at the object level (DRF calls this automatically after get_object)
#         # self.check_object_permissions(self.request, obj)
#
#         if not obj.profile.is_complete:
#              # --- Keep your unconventional 200 OK response for incomplete profile ---
#              # This check happens *after* the object is found and permissions are checked.
#              # It's unusual to return a 200 OK error this way, but preserving your logic.
#              return Response({
#                 "success": False,
#                 "is_completed": False,
#                 "message": "ابتدا باید پروفایل خود را تکمیل کنید."
#             }, status=status.HTTP_200_OK)
#
#         return obj # Return the found and (potentially) complete object
#
#     # --- get_serializer_context, retrieve, update methods remain as you provided ---
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context
#
#     def retrieve(self, request, *args, **kwargs):
#         instance_or_response = self.get_object()
#         if isinstance(instance_or_response, Response):
#             return instance_or_response
#         instance = instance_or_response
#         serializer = self.get_serializer(instance)
#         return Response({
#             "success": True,
#             "data": serializer.data,
#             "message": "پنل فروشگاه با موفقیت دریافت شد."
#         }, status=status.HTTP_200_OK)
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance_or_response = self.get_object()
#         if isinstance(instance_or_response, Response):
#             return instance_or_response
#         instance = instance_or_response
#
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         is_valid = serializer.is_valid()
#         if is_valid:
#             self.perform_update(serializer)
#             return Response({
#                 "success": True,
#                 "data": serializer.data,
#                 "message": "فروشگاه با موفقیت بروز رسانی شد."
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "success": False,
#                 "error": serializer.errors,
#                 "message": "اطلاعات وارد شده معتبر نیست. لطفا خطاها را بررسی کنید."
#             }, status=status.HTTP_400_BAD_REQUEST)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# shop type and monetary unit choices
class ShopChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        shop_type_choices = [
            {"value": key, "label": label} for key, label in Shop.SHOP_TYPE_CHOICES
        ]
        monetary_unit_choices = [
            {"value": key, "label": label} for key, label in Shop.MONETARY_UNIT_CHOICES
        ]
        Response.message = 'مقادیر انتخاب فراخوانی شدند.'
        return Response({
            "shop_type_choices": shop_type_choices,
            "monetary_unit_choices": monetary_unit_choices
        })

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# open days and hours
class ShopWeeklyPlanAPIView(APIView):
    """
    APIView for managing the shop's weekly schedule.
    GET: Returns the current list of open days with their open hours.
    POST: Creates new open day records (with nested open hours) for the shop.
          The day ID is not provided by the user; it is created automatically.
    """
    permission_classes = [IsShopOwnerOrAdmin]

    @swagger_auto_schema(
        responses={200: ShopWeeklyPlanSerializer()},
    )
    def get(self, request, format=None):
        try:
            shop = request.user.shopprofile.shop
            data = {"open_days": shop.open_days.all()}
            serializer = ShopWeeklyPlanSerializer(instance=data, context={'shop': shop})
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "برنامه هفتگی فروشگاه با موفقیت دریافت شد."
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            # Customize the error response
            return Response({
                "success": False,
                "data": {},
                "error": str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=ShopWeeklyPlanSerializer,
        responses={201: ShopWeeklyPlanSerializer()}
    )
    def post(self, request, format=None):
        shop = request.user.shopprofile.shop
        serializer = ShopWeeklyPlanSerializer(data=request.data, context={'shop': shop})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "برنامه هفتگی فروشگاه با موفقیت ایجاد شد."
            }, status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response({
                "success": False,
                "data": {},
                "error": exc.detail  # exc.detail preserves error details as structured data
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({
                "success": False,
                "data": {},
                "error": str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)


class ShopOpenHoursDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific open hour record.
    PATCH/PUT: Update the open_time and/or close_time.
    DELETE: Delete the open hour record.

    Only open hours belonging to the current shop (via the user's ShopProfile) are allowed.
    """
    serializer_class = ShopOpenHoursSerializer
    permission_classes = [IsShopOwnerOrAdmin]

    def get_queryset(self):
        # Short-circuit for schema generation tools
        if getattr(self, 'swagger_fake_view', False):
            return ShopOpenHours.objects.none()

        user = self.request.user

        # If the user is anonymous or doesn't have a shopprofile, return an empty queryset.
        if not user.is_authenticated or not hasattr(user, 'shopprofile'):
            return ShopOpenHours.objects.none()

        shop = user.shopprofile.shop
        # Return open hours for any open day of that shop.
        return ShopOpenHours.objects.filter(day__shop=shop)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "اطلاعات ساعت‌های کاری با موفقیت دریافت شد."
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "اطلاعات ساعت‌های کاری با موفقیت به‌روز رسانی شد."
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "data": {},
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "data": {},
            "message": "ساعت کاری با موفقیت حذف شد."
        }, status=status.HTTP_204_NO_CONTENT)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Delete any rejected item of shop profile by admin
class ClearProfileAttributeView(generics.GenericAPIView):
    serializer_class = ClearProfileAttributeSerializer
    permission_classes = [IsAdminUser]  # Admins only

    def post(self, request, *args, **kwargs):
        # Get the shop_id from the URL.
        shop_id = kwargs.get('shop_id')
        if not shop_id:
            return Response({
                "success": False,
                "message": "شناسه فروشگاه مشخص نشده است."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the Shop based on the shop_id.
        shop = get_object_or_404(Shop, id=shop_id)
        # Access the corresponding ShopProfile and its owner.
        profile = shop.profile
        owner = profile.owner

        # Validate the incoming data using the serializer.
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "داده‌های ارسال شده معتبر نیستند.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Map the attribute to the proper model/field.
        attribute = serializer.validated_data['attribute']
        target_model, field = serializer.map_attribute_to_model(attribute)

        if target_model == "profile":  # Clear the field on ShopProfile.
            old_value = getattr(profile, field, None)
            setattr(profile, field, None)
            profile.save()
        elif target_model == "owner":  # Clear the field on the owner (User).
            old_value = getattr(owner, field, None)
            setattr(owner, field, None)
            owner.save()
            # Optionally save the profile to trigger any post-save signal.
            profile.save()
        else:
            return Response({
                "success": False,
                "message": f"ویژگی '{attribute}' یافت نشد."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": f"ویژگی '{attribute}' با موفقیت حذف شد.",
            "previous_value": old_value
        })

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# File manager
class ShopMediaFilesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows shop media files to be viewed, uploaded, edited and deleted.
    For list, create, retrieve, and update:
      - The shop owner (as determined by the shop profile owner) has access.
    For destroy (delete):
      - Only a superuser or staff is allowed.
    """
    serializer_class = ShopMediaFilesSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['media_type', 'is_global']
    search_fields = ['media_type']

    def get_queryset(self):
        # Check if this is a schema generation request or the user is not authenticated.
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return ShopMediaFiles.objects.none()

        # Superusers (or staff) see everything.
        if self.request.user.is_staff or self.request.user.is_superuser:
            return ShopMediaFiles.objects.all()

        # For normal shop owners, show files belonging to them or files marked as global.
        return ShopMediaFiles.objects.filter(
            Q(shop__profile__owner=self.request.user.id) | Q(is_global=True)
        )

    def get_permissions(self):
        if self.action == "destroy":
            # For deletion, restrict access further.
            permission_classes = [permissions.IsAdminUser]
        else:
            # For all other actions, enforce that the user is either the shop owner or an admin.
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
                'is_global',
                openapi.IN_QUERY,
                description='Filter files by global flag (true/false)',
                type=openapi.TYPE_BOOLEAN
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Override list() to return files in the envelope.
        """
        # Apply filtering / search.
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = self.get_queryset()

        # Split the queryset.
        global_files_qs = queryset.filter(is_global=True)
        local_files_qs = queryset.exclude(is_global=True)

        # Serialize them.
        global_serialized = self.get_serializer(global_files_qs, many=True).data
        shop_serialized = self.get_serializer(local_files_qs, many=True).data

        # Group the serialized data by media_type.
        grouped_global_files = self._group_by_media_type(global_serialized)
        grouped_local_files = self._group_by_media_type(shop_serialized)

        response_data = {
            "global_files": grouped_global_files,
            "local_files": grouped_local_files,
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.message = "فایل‌ها با موفقیت فراخوانی شدند."
        return response

        # return Response({
        #     "success": True,
        #     "data": response_data,
        #     "message": "فایل‌ها با موفقیت فراخوانی شدند."
        # }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Override create() to return the created file in the envelope.
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
        Override destroy() to delete a file record and return the envelope.
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

# Media Type Choices
class ShopMediaTypeChoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        choices = [
            {"value": choice[0], "label": choice[1]}
            for choice in ShopMediaFiles.MEDIA_TYPE_CHOICES
        ]
        Response.message = 'مقادیر انتخاب فراخوانی شدند.'
        return Response({"choices": choices})

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# shop dashboard view
class ShopDashboardView(APIView):
    # permission_classes = [IsShopOwnerOrAdmin]
    #
    # def get_object(self):
    #     shop = get_object_or_404(Shop, profile__owner=self.request.user)
    #     # Enforce profile verification:
    #     if not shop.profile.is_complete:
    #         data = {"is_complete": shop.profile.is_complete}
    #         # raise PermissionDenied("ابتدا باید پروفایل خود را تکمیل و تأیید کنید.")
    #         return Response({
    #             "success": False,
    #             "is_complete": shop.profile.is_complete,
    #             # "data": data,
    #             "error": "ابتدا باید پروفایل خود را تکمیل و تأیید کنید."
    #         }, status=status.HTTP_403_FORBIDDEN)  # Use appropriate HTTP status code for permission issues
    #     return shop
    #
    # def get(self, request, *args, **kwargs):
    #     shop_response = self.get_object()
    #     if isinstance(shop_response, Response):  # Check if `get_object` returned a Response
    #         return shop_response
    #
    #     serializer = ShopDashboardSerializer(shop_response, context={"request": request})
    #     return Response({
    #         "success": True,
    #         "data": serializer.data,
    #         "message": "داشبورد فروشگاه با موفقیت دریافت شد."
    #     }, status=status.HTTP_200_OK)
    pass


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# --------------------------------------------------------------------------
# Cafe Manu
# class CafeMenuApiView(APIView):
#     def get(self, request, shop_id):
#         shop = get_object_or_404(Shop, id=shop_id)
#
#         # Fetch products
#         products = Product.objects.filter(shop=shop, is_active=True, is_wholesale=False)
#         product_serializer = ProductSerializer(products, many=True, context={'request': request})
#
#         # Fetch product bundles
#         bundles = ProductBundle.objects.filter(shop=shop, is_active=True)
#         bundle_serializer = ProductBundleSerializer(bundles, many=True)
#
#         # Check for special products
#         special_exists = products.filter(is_special=True).exists()
#
#         # Create response context
#         context = {
#             'products': product_serializer.data,
#             'bundles': bundle_serializer.data,
#             'special_exists': special_exists
#         }
#
#         return Response(context, status=status.HTTP_200_OK)


# --------------------------------------------------------------------------
# Single Product
# class ProductViewSet(viewsets.ModelViewSet):
#     serializer_class = ProductSerializer
#
#     def get_queryset(self):
#         shop_id = self.kwargs.get('shop_id')
#         if shop_id:
#             return Product.objects.filter(shop_id=shop_id)
#         return Product.objects.none()  # Return an empty queryset if no shop_id is provided
