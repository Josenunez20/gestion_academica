from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal.accounts'   # ← Cambiar de 'accounts' a 'personal.accounts'