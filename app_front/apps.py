from django.apps import AppConfig


class AppFrontConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_front'

    def ready(self):
        import app_front.signals
