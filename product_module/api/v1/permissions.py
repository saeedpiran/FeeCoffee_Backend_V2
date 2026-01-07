from rest_framework import permissions, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.author == request.user


class IsAdminOrSuperuserOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins or superusers to edit, but read for everyone.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class IsShopOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to the shop owner or administrators.
    Assumes that:
      - For a ShopWeeklyPlanAPIView (which works on a composite dict), only view-level permissions are checked.
      - For object-level permissions (like in ShopOpenHoursDetailAPIView), the object is expected to have a
        'day' attribute linking to a ShopOpenDays instance.
    """

    def has_permission(self, request, view):
        # User must be authenticated.
        if not (request.user and request.user.is_authenticated):
            return False
        # Admin users get full access.
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Regular users must have a shopprofile and shop.
        return hasattr(request.user, 'shopprofile') and hasattr(request.user.shopprofile, 'shop')

    def has_object_permission(self, request, view, obj):
        # Admin setting
        if request.user.is_staff or request.user.is_superuser:
            return True

        # For ShopOpenHours objects, traverse through the "day" relation:
        if hasattr(obj, 'day'):
            # Ensure that the object’s day relationship exists, then check ownership.
            return obj.day.shop.profile.owner == request.user

        # If for some reason the object has a direct "shop" attribute, try that.
        if hasattr(obj, 'shop'):
            return obj.shop.profile.owner == request.user

        # Otherwise, deny access.
        return False
# -------------------------------------------------------------
# Custom PermissionDenied
class CustomPermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'permission_denied'

    def __init__(self, detail):
        # Do not call the parent's __init__ to avoid any conversion.
        self.detail = detail
