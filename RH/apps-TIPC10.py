from django.apps import AppConfig


class RhConfig(AppConfig):
    name = 'RH'
    
    def ready(self):
        """Registra signals quando a app está pronta"""
        import RH.signals
