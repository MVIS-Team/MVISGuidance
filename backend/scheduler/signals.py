from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from scheduler.models import Session

if TYPE_CHECKING:
    from typing import Type


@receiver(post_save, sender=Session)
def session_permission(
    sender: Type[Session],
    instance: Session,
    created: bool,
    **kwargs,
):  # pylint: disable=W0613
    if created:
        assign_perm("scheduler.change_session", instance.student, instance)
        assign_perm("scheduler.delete_session", instance.student, instance)
        assign_perm("scheduler.view_session", instance.student, instance)
        assign_perm("scheduler.change_session", instance.teacher, instance)
        assign_perm("scheduler.delete_session", instance.teacher, instance)
        assign_perm("scheduler.view_session", instance.teacher, instance)
