from rest_framework import permissions


# Allow only 'GET', 'HEAD', 'OPTIONS' for any.
class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class DeleteProhibition(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT')
