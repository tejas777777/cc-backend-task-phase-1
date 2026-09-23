from rest_framework.permissions import BasePermission

from .models import Profile


def _has_role(user, role):
    return bool(user and user.is_authenticated and getattr(user, 'profile', None) and user.profile.role == role)


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, Profile.Role.BUYER)


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, Profile.Role.SELLER)


class IsItemOwner(BasePermission):
    """Object-level check restricting a seller to their own items."""

    def has_object_permission(self, request, view, obj):
        return obj.seller_id == request.user.id
