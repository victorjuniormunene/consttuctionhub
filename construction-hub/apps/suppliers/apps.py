from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.suppliers'

    def ready(self):
        # Import signals to ensure they are registered
        try:
            import apps.suppliers.signals  # noqa: F401
        except Exception:
            pass
