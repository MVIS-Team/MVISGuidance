from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.contrib import auth
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible

if TYPE_CHECKING:
    from typing import Callable, Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


@deconstructible
class ProfileUploadPath:  # pylint: disable=R0903
    def __call__(self, instance: Profile, filename: str) -> str:
        return f"profile/{instance.user.pk}-{filename}"


profile_upload_path: Callable[[Profile, str], str] = ProfileUploadPath()


class Profile(models.Model):
    """Default profile for Tutor Scheduler."""

    #: First and last name do not cover name patterns around the globe
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to=cast(
            "Callable[[models.Model, str], str]",
            profile_upload_path,
        ),
        blank=True,
    )

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse(
            "users:redirect",
            kwargs={
                "username": self.user.username,
            },
        )

    def __str__(self):
        return self.name

    @property
    def name(self):
        return (
            f"{self.user.first_name} {self.user.last_name}"
            if self.user.first_name and self.user.last_name
            else self.user.username
        )

    @property
    def avatar_url(self):
        if self.user.is_superuser:
            return settings.ADMIN_PROFILE
        return (
            self.avatar.url  # pylint: disable=E1101
            if self.avatar
            else settings.DEFAULT_PROFILE
        )
