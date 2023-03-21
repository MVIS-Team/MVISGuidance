from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_objects_for_user
from users.forms import ProfileChangeForm
from users.models import Profile

if TYPE_CHECKING:
    from typing import Any


# Create your views here.
@login_required
def profile_detail_view(request, **kwargs):
    profile = Profile.objects.get(user__username=kwargs["username"])
    user = request.user
    sessions = get_objects_for_user(
        user, "scheduler.view_session", with_superuser=False
    )
    return render(
        request,
        "users/profile.html",
        context={
            "profile": profile,
            "user": user,
            "teacher_sessions": sessions.filter(teacher=profile.user),
            "student_sessions": sessions.filter(student=profile.user),
        },
    )


@login_required
def profile_update_view(request):
    context: dict[str, Any] = {}
    profile = request.user.profile
    if request.POST:
        form = ProfileChangeForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully update profile!")
            return redirect(profile)
        for field, errors in form.errors.as_data().items():
            for error in errors:
                messages.error(request, f"{field}: {error.message}")
    form = ProfileChangeForm(instance=profile)
    context["form"] = form
    return render(request, "users/profile_update.html", context)


@login_required
def profile_redirect_view(request, **kwargs):
    username: str
    if "username" in kwargs:
        username = kwargs["username"]
    else:
        username = request.user.username
    return redirect("users:detail", username=username, permanent=False)
