"""
Utilidades de autenticación y autorización.
"""

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def requiere_rol(*roles):
    """
    Decorador que restringe el acceso a una vista según el rol del usuario.

    Uso:
        @login_required(login_url='login')
        @requiere_rol('admin')
        def mi_vista(request): ...

        @login_required(login_url='login')
        @requiere_rol('admin', 'vendedor')
        def otra_vista(request): ...

    Args:
        *roles: Roles permitidos ('admin', 'vendedor', 'cliente').
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = getattr(request.user, 'role', None)
            if user_role is None or user_role.role not in roles:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
