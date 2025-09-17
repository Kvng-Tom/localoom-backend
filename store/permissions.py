from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsArtisan(BasePermission):
    """
    Allows access only to users with role=ARTISAN.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ARTISAN"


class IsBuyerOrReadOnly(BasePermission):
    """
    Buyers can only read storefronts/products.
    Artisans/Admins can edit their own.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ["ARTISAN", "ADMIN"]
