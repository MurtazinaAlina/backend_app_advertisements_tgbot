from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        elif request.user.is_staff:  # Открытие доступа для администратора
            return True

        return request.user == obj.creator  # Открытие доступа для владельца


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):  # только для ретрив-логики

        if request.user.is_staff:  # Открытие доступа для администратора
            return True

        return request.user == obj.user
