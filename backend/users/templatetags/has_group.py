from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

register = template.Library()

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


@register.filter(name="has_group")
def has_group(user: AbstractUser, group_name: str):
    return user and group_name and user.groups.filter(name=group_name).exists()
