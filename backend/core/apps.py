from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração da aplicação Django 'core'.

    Define a aplicação principal onde estão os modelos,
    views e rotas do sistema.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
