from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.account and request.user.account.is_admin