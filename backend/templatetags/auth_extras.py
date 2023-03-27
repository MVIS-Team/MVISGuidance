from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

register = template.Library()


@register.filter(name="has_group")
def has_group(user: AbstractUser, group_name: str):  # pylint: disable=E0601
    return user.groups.filter(name=group_name).exists()
