from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from typing import Any

    from users.models import Profile

register = template.Library()


@register.inclusion_tag(
    "users/profile_detail.html", name="profile_detail", takes_context=True
)
def profile_detail(
    context: dict[str, Any],
    profile: Profile,
):
    return {
        "profile": profile,
        "user": context.get("user"),
    }
