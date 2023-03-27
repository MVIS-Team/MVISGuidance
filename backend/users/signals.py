from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import auth
from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from users.models import Profile

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


@receiver(post_save, sender=User)
def save_profile(
    sender: Type[AbstractUser],
    instance: AbstractUser,
    created: bool,
    **kwargs,
):  # pylint: disable=W0613
    if created:
        Profile.objects.get_or_create(user=instance)
    profile: Profile = instance.profile  # type: ignore
    profile.save()


@receiver(post_save, sender=User)
def set_permission(
    sender: Type[AbstractUser],
    instance: AbstractUser,
    created: bool,
    **kwargs,
):  # pylint: disable=W0613
    if created:
        assign_perm("scheduler.add_session", instance)
        teacher_group, created = Group.objects.get_or_create(name="teacher")
        assign_perm("auth.view_group", instance, teacher_group)


@receiver(post_delete, sender=User)
def delete_profile(
    sender: Type[AbstractUser],
    instance: AbstractUser,
    **kwargs,
):  # pylint: disable=W0613
    profile: Profile = instance.profile  # type: ignore
    profile.delete()
