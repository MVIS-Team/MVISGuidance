from __future__ import annotations

from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from scheduler.models import Session


# Register your models here.
class SessionAdmin(GuardedModelAdmin):
    pass


admin.site.register(Session, SessionAdmin)
