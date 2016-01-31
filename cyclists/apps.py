from django.apps import AppConfig

class cyclistsConfig(AppConfig):
    name = 'cyclists'

    def ready(self):
        super(cyclistsConfig,self).ready()
        import signals.handlers



