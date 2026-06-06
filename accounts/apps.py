from django.apps import AppConfig


class AccountsConfig(AppConfig):
    defalut_aute_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals

