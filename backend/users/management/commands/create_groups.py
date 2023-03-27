from __future__ import annotations

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initialize user group(s)"

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name="teacher")
