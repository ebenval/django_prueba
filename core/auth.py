"""
Utilidades de autenticación y autorización.
"""

from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden


def create_user_groups():
    """
    Crea los grupos de usuarios predefinidos.
    """
    groups = ['Editores', 'Moderadores', 'Visitantes']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)


def check_user_permission(user, permission_name):
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user (User): El usuario a verificar.
        permission_name (str): Nombre del permiso (ej: 'auth.add_user').
    
    Returns:
        bool: True si el usuario tiene el permiso, False en caso contrario.
    """
    return user.has_perm(permission_name)


def add_user_to_group(user, group_name):
    """
    Añade un usuario a un grupo.
    
    Args:
        user (User): El usuario a añadir.
        group_name (str): Nombre del grupo.
    
    Returns:
        Group: El grupo al que se añadió el usuario.
    """
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    return group
