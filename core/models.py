"""
Modelos de la aplicación core.
"""

from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """
    Modelo base con timestamps para otros modelos.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """
    Perfil extendido del usuario.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
