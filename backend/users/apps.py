from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = _("Users")

    def ready(self):
        import users.signals  # noqa # pylint: disable=C0415,W0611
