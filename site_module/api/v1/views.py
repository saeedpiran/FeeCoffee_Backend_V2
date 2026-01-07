from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response

from site_module.models import SiteSetting
from .permissions import IsAdminOrSuperuserOrReadOnly  # Import the custom permission class
from .serializers import SiteSettingsSerializer


class SiteSettingsApiViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSettingsSerializer
    queryset = SiteSetting.objects.all()
    permission_classes = [IsAdminOrSuperuserOrReadOnly]  # Apply the custom permission class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "اطلاعات سایت با موفقیت دریافت شد."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "اطلاعات سایت با موفقیت دریافت شد."
        }, status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if isinstance(exc, PermissionDenied):
            response.data = {
                "success": False,
                "data": {},
                "error": "شما دسترسی لازم برای انجام این عملیات را ندارید."
            }
            response.status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, NotAuthenticated):
            response.data = {
                "success": False,
                "data": {},
                "error": "شما وارد سیستم نشده اید."
            }
            response.status_code = status.HTTP_401_UNAUTHORIZED
        else:
            response.data = {
                "success": False,
                "data": {},
                "error": response.data.get('error', str(exc))
            }

        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "مجموعه اطلاعات جدید برای سایت با موفقیت ایجاد شد."
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "success": True,
                "data": serializer.data,
                "message": "اطلاعات سایت با موفقیت بروزرسانی شد."
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "مجموعه اطلاعات سایت با موفقیت حذف شد."
        }, status=status.HTTP_204_NO_CONTENT)
