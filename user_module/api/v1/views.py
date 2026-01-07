from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict, Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from accounts_module.models import UserMediaFiles
from user_module.models import UserProfile, StoredLocation
from .permissions import IsOwner
from .serializers import StoredLocationSerializer
from .serializers import UserProfileSerializer


# class UserProfileApiView(generics.RetrieveUpdateAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsOwner]  # Ensure the user is authenticated and is the owner
#     serializer_class = UserProfileSerializer
#     queryset = UserProfile.objects.all()
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         obj = get_object_or_404(queryset, owner=self.request.user)
#         return obj
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#
#         try:
#             # Create a mutable copy of request.data
#             if isinstance(request.data, QueryDict):
#                 data = request.data.dict()
#             else:
#                 data = request.data.copy()
#
#             # Validate and update the UserProfile model fields
#             serializer = self.get_serializer(instance, data=data, partial=partial)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "success": True,
#                     "data": serializer.data,
#                     "message": "پروفایل کاربر با موفقیت بروز رسانی شد."
#                 }, status=status.HTTP_200_OK)
#             else:
#                 return Response({
#                     "success": False,
#                     "error": serializer.errors
#                 }, status=status.HTTP_400_BAD_REQUEST)
#
#
#
#         except Exception as e:
#             # Return an error response
#             return Response({
#                 "success": False,
#                 "error": f"خطا رخ داده است: {str(e)}"
#             }, status=status.HTTP_400_BAD_REQUEST)


class StoredLocationViewSet(viewsets.ModelViewSet):
    queryset = StoredLocation.objects.all()
    serializer_class = StoredLocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]  # Ensure the user is authenticated and is the owner

    def get_queryset(self):
        # Short-circuit schema generation for Swagger
        if getattr(self, 'swagger_fake_view', False):
            return StoredLocation.objects.none()

        user = self.request.user

        # Ensure the user is authenticated
        if isinstance(user, AnonymousUser):
            raise Http404("کاربر اعتبارسنجی نشده است.")

        # Check the user's role and handle accordingly
        if user.user_type == 'customer':
            user_profile = get_object_or_404(UserProfile, owner=user)
            return user_profile.stored_locations.all()
        elif user.user_type in ['seller', 'admin']:
            raise Http404("برای ادمین و فرشگاه ها مکانهای ذخیره شده وجود ندارد.")
        else:
            raise Http404("نوع کاربر قابل تشخیص نیست.")

    def perform_create(self, serializer):
        user_profile = get_object_or_404(UserProfile, owner=self.request.user)
        serializer.save(user_profile=user_profile)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "success": True,
            "data": response.data,
            "message": "موقعیت مورد نظر با موفقیت ایجاد شد."
        }
        return Response(response.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            "success": True,
            "data": response.data,
            "message": "موقعیت مورد نظر با موفقیت بروز رسانی شد."
        }
        return Response(response.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": '',
            "message": "موقعیت مورد نظر با موفقیت حذف شد."
        }, status=status.HTTP_204_NO_CONTENT)





# ------------------------------------------------------------
class UserProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]  # IsOwner should verify obj.owner == request.user
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_object(self):
         # Fetch the UserProfile for the current authenticated user.
         return get_object_or_404(self.get_queryset(), owner=self.request.user)

    def update(self, request, *args, **kwargs):
         partial = kwargs.pop('partial', False)
         instance = self.get_object()

         serializer = self.get_serializer(instance, data=request.data, partial=partial)
         if serializer.is_valid():
              serializer.save()
              return Response({
                  "success": True,
                  "data": serializer.data,
                  "message": "پروفایل کاربر با موفقیت بروز رسانی شد."
              }, status=status.HTTP_200_OK)
         return Response({
              "success": False,
              "error": serializer.errors
         }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------
# # user avatar manager
# class UserAvatarViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows a user to view, upload, edit, and delete their avatar.
#     Only authenticated users can perform these operations. Staff and superusers can see all avatars.
#     """
#     serializer_class = UserAvatarManageSerializer
#
#     def get_queryset(self):
#         # Superusers and staff may view any avatar records.
#         if self.request.user.is_staff or self.request.user.is_superuser:
#             return UserMediaFiles.objects.filter(media_type=UserMediaFiles.AVATAR)
#         # Otherwise, return only avatar records belonging to the authenticated user.
#         return UserMediaFiles.objects.filter(user=self.request.user, media_type=UserMediaFiles.AVATAR)
#
#     def get_permissions(self):
#         # For this endpoint, only require that the user is authenticated.
#         permission_classes = [permissions.IsAuthenticated]
#         return [permission() for permission in permission_classes]
#
#     def perform_create(self, serializer):
#         # Ensure that on creation, the media type is set to avatar and the file is associated with the current user.
#         serializer.save(user=self.request.user, media_type=UserMediaFiles.AVATAR)