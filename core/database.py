"""
Configuración y utilidades para la base de datos.
"""

from django.db import connections
from django.db.utils import OperationalError


def check_database_connection():
    """
    Verifica si la base de datos está disponible.
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario.
    """
    try:
        connection = connections['default']
        connection.ensure_connection()
        return True
    except OperationalError:
        return False


def init_db():
    """
    Inicializa la base de datos con datos por defecto (si es necesario).
    """
    from django.contrib.auth.models import User
    from .models import Profile

    # Crear superusuario por defecto si no existe
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
        Profile.objects.create(
            user=admin,
            bio='Administrador del sitio'
        )
