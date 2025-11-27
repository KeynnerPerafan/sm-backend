from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Distribuidor

Usuario = get_user_model()

@receiver(post_save, sender=Usuario)
def ensure_distribuidor_for_vendedor(sender, instance, created, **kwargs):
    """
    - Si el usuario es 'vendedor', aseguremos que tenga registro de Distribuidor.
    - Si cambia su rol a 'vendedor' (no solo al crearse), también lo creamos si falta.
    """
    if getattr(instance, "rol", None) == "vendedor":
        Distribuidor.objects.get_or_create(user=instance)
