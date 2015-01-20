from django.apps import AppConfig


class ShiftConfig(AppConfig):
    name = 'apps.shifts'
    verbose_name = 'Shifts'

    def ready(self):
        import apps.shifts.signals
        pass