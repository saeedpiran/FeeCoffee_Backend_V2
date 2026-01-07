from rest_framework import permissions


class IsShopOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to the shop owner or administrators.
    """

    def has_permission(self, request, view):
        # User must be authenticated.
        if not (request.user and request.user.is_authenticated):
            # DRF's authentication framework usually handles 401,
            # but returning False here explicitly denies if not authenticated.
            return False
        # Admin users get full access.
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Regular users must have a shopprofile and shop to even pass view-level permission for this API
        # This prevents random authenticated users from potentially accessing the view that expects a shop owner.
        # However, the object-level permission is the primary check for correctness.
        return hasattr(request.user, 'shopprofile') and hasattr(request.user.shopprofile, 'shop')


    def has_object_permission(self, request, view, obj):
        # Admin setting
        if request.user.is_staff or request.user.is_superuser:
            return True

        # --- FIX: Add check for the Shop object itself ---
        # Check if the object is a Shop instance and if the requesting user is the owner
        # Assuming 'Shop' is the name of your Shop model class
        # You might need to import your Shop model if not already in scope
        try:
            # Check if obj is a Shop instance or can be treated as one for ownership check
            # The obj in this view is guaranteed to be a Shop instance.
            if hasattr(obj, 'profile') and hasattr(obj.profile, 'owner'):
                 return obj.profile.owner == request.user
        except AttributeError:
             # This catch is mostly for safety if obj structure is unexpected
             pass

        # --- Keep checks for related objects, but they won't apply to the main Shop object in this view ---
        # For ShopOpenHours objects, traverse through the "day" relation:
        if hasattr(obj, 'day'):
            # Ensure that the object’s day relationship exists, then check ownership.
            if hasattr(obj.day, 'shop') and hasattr(obj.day.shop, 'profile') and hasattr(obj.day.shop.profile, 'owner'):
                return obj.day.shop.profile.owner == request.user

        # If for some reason the object has a direct "shop" attribute, try that.
        # This might apply to things like ShopMediaFiles related directly to a shop
        if hasattr(obj, 'shop'):
             if hasattr(obj.shop, 'profile') and hasattr(obj.shop.profile, 'owner'):
                 return obj.shop.profile.owner == request.user


        # If none of the specific checks pass, deny access.
        return False

