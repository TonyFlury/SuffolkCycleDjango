from django.apps import AppConfig
from threading import Timer
import os


def run_scheduler():
    import scheduler # Run time import - can't import before the models are ready.
    scheduler.start_scheduler()


class EmailplusConfig(AppConfig):
    name = 'EmailPlus'
    def ready(self):
        if os.getenv("DJANGO_MANAGEMENT", "False") == "False":
            # Crude - but defer start of scheduler for 5 minutes to allow management commands to run
            # Can't run the scheduler directly as the models don't become ready when the App is ready
            # and AppRegistryNotReady Exception is raised
            # https://docs.djangoproject.com/en/1.9/ref/applications/#initialization-process
            Timer(300,run_scheduler).start()
