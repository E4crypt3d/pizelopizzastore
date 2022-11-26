from django.apps import AppConfig


class PizzastoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pizzastore'
    
    def ready(self):
        import pizzastore.signals
