from django.apps import AppConfig


class FillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.filling'
    verbose_name = 'Подача заявок'

    def ready(self):
        from . import signals
