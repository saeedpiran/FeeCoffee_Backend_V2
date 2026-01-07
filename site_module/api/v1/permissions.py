from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperuserOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins or superusers to edit, but read for everyone.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

# from rest_framework.permissions import BasePermission
#
# class IsAdminOrSuperuser(BasePermission):
#     """
#     Custom permission to only allow site admins or superusers to access the view.
#     """
#     def has_permission(self, request, view):
#         return request.user and (request.user.is_staff or request.user.is_superuser)
