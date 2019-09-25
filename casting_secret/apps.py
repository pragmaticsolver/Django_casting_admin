from django.apps import AppConfig


class CastingSecretConfig(AppConfig):
    name = 'casting_secret'

    def ready(self):
        from casting_secret import Signals
