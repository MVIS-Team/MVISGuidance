from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from typing import Any, Literal

    from scheduler.models import Session

register = template.Library()


@register.inclusion_tag(
    "scheduler/session_detail.html", name="session_detail", takes_context=True
)
def session_detail(
    context: dict[str, Any],
    session: Session,
    mode: Literal["teacher", "student"] = "student",
):
    return {
        "session": session,
        "user": context["user"],
        "mode": mode,
    }
