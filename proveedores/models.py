from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    # Campo de iniciales para numeración de pedido
    iniciales = models.CharField(max_length=10, blank=True, default="")

    # Estado del proveedor
    activo = models.BooleanField(default=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    # Generar iniciales automáticamente
    def save(self, *args, **kwargs):
        if not self.iniciales or self.iniciales.strip() == "":
            palabras = self.nombre.split()

            if len(palabras) == 1:
                self.iniciales = palabras[0][:2].upper()
            else:
                self.iniciales = "".join(p[0] for p in palabras).upper()[:4]

        super().save(*args, **kwargs)
