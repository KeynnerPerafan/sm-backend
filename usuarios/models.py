from datetime import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Use solo dígitos y opcional + al inicio (7–15 dígitos).",
)

class Usuario(AbstractUser):

    # Sobrescribimos username para permitir espacios
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Nombre de usuario con espacios permitido.",
    )

    email = models.EmailField(unique=True)

    rol = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Administrador'),
            ('distribuidor', 'Distribuidor'),
            ('cliente', 'Cliente'),
        ],
        default='cliente',
    )

    whatsapp = models.CharField(max_length=20, blank=True, validators=[phone_validator])
    telefono = models.CharField(max_length=20, blank=True, validators=[phone_validator])

    def __str__(self):
        return f"{self.username} ({self.rol})"

    fecha_registro = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.fecha_registro:
            self.fecha_registro = timezone.now().date()
        super().save(*args, **kwargs)