from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

register = template.Library()

if TYPE_CHECKING:
    from django.contrib.auth.models import User


@register.filter(name="has_group")
def has_group(user: User, group_name: str):
    if not user or not group_name:
        return False
    return user.groups.filter(name=group_name).exists()
