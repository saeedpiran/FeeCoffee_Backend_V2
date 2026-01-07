from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.author == request.user


# -----------------------------------------------------------------------
# file manager
class IsArticleOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for ArticleMediaFiles:
      - SAFE_METHODS: allowed for any authenticated user.
      - Create/Update: allowed only if the file's owner (file.user) equals request.user.
      - Delete: allowed only for admin/staff.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for any authenticated user.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admin/staff have full rights.
        if request.user.is_superuser or request.user.is_staff:
            return True
        # For create or update, check if the file's owner is the same as the request user.
        return obj.user == request.user
