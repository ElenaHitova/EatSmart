from rest_framework.permissions import SAFE_METHODS, BasePermission
from accounts.roles import can_manage_food_catalog


class CanManageFoodCatalogForWrite(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return can_manage_food_catalog(request.user)
