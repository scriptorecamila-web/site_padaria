from django.apps import AppConfig


class ConfeitariaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "confeitaria"
    verbose_name = "Confeitaria"

    def ready(self):
        from .signals import conectar

        conectar()
