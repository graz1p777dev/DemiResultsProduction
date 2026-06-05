from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role in self.allowed_roles)
        )


class IsOwnerAdminManager(RolePermission):
    allowed_roles = {"OWNER", "ADMIN", "MANAGER"}


class IsStaffOperator(RolePermission):
    allowed_roles = {"OWNER", "ADMIN", "MANAGER", "CASHIER", "WAREHOUSE"}


class IsSalesOperator(RolePermission):
    allowed_roles = {"OWNER", "ADMIN", "MANAGER", "CASHIER"}


class IsInventoryOperator(RolePermission):
    allowed_roles = {"OWNER", "ADMIN", "MANAGER", "WAREHOUSE"}


class IsClient(RolePermission):
    allowed_roles = {"CLIENT"}
