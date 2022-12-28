from __future__ import annotations

import os
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.contrib import auth
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from typing import Callable, Type

    from django.contrib.auth.models import User as _User

    from users.models import Profile as _Profile

# Create your models here.
User: Type[_User] = cast("Type[_User]", auth.get_user_model())


@deconstructible
class ProfileUploadPath:
    def __call__(self, instance: _Profile, filename: str) -> str:
        return f"profile/{instance.user.pk}-{filename}"


profile_upload_path: Callable[[models.Model, str], str] = ProfileUploadPath()


class Profile(models.Model):
    """Default profile for Tutor Scheduler."""

    #: First and last name do not cover name patterns around the globe
    user: models.OneToOneField = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(
        upload_to=profile_upload_path,
        blank=True,
    )

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:redirect", kwargs={"username": self.user.username})

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
        return self.avatar.url if self.avatar else settings.DEFAULT_PROFILE
