from django.apps import AppConfig


class ScontriniConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scontrini'

    # caricamento segnale
    def ready(self):
        import scontrini.signals
