from rest_framework.permissions import BasePermission


class AdminUserPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin
