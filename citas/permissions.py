# permissions for role-based access

from rest_framework import permissions
from .models import rol

class IsPaciente(permissions.BasePermission):
    """Allow access only to users with role 'paciente'"""
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.id_rol and user.id_rol.nombre == 'paciente')

class IsMedico(permissions.BasePermission):
    """Allow access only to users with role 'medico'"""
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.id_rol and user.id_rol.nombre == 'medico')

class IsAdmin(permissions.BasePermission):
    """Allow access only to users with role 'admin'"""
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.id_rol and user.id_rol.nombre == 'admin')
