from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import admin, auth
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from users.forms import ProfileChangeForm, UserChangeForm, UserCreationForm
from users.models import Profile

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet
    from django.http import HttpRequest

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


admin.site.unregister(User)
# admin.site.register(Profile)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileChangeForm
    list_display = ["name", "user"]


@admin.register(User)
class UserAdmin(_UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("email", "first_name", "last_name")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "is_superuser"]
    inlines = (ProfileInline,)
    search_fields = ["username"]
    actions = ["make_teacher"]

    @admin.action(description="Set user as teacher")
    def make_teacher(self, request: HttpRequest, queryset: QuerySet[AbstractUser]):
        teacher, _ = Group.objects.get_or_create(name="teacher")
        teachers: RelatedManager[AbstractUser] = teacher.user_set  # type: ignore
        teachers.add(*queryset)
