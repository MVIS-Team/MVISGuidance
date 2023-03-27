from __future__ import annotations

from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scheduler"

    def ready(self):
        import scheduler.signals  # noqa # pylint: disable=C0415,W0611
