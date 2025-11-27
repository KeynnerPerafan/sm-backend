from django.apps import AppConfig

class DistribuidoresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "distribuidores"

    def ready(self):
        from . import signals  # noqa
