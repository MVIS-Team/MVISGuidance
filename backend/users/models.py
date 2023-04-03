from __future__ import annotations
import os

from typing import TYPE_CHECKING, cast
from urllib.request import urlretrieve

from django.conf import settings
from django.contrib import auth
from django.db import models
from django.core.files import File
from django.urls import reverse
from PIL import Image

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="profile",
        blank=True,
    )

    def get_absolute_url(self):
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
        return self.avatar.url  # pylint: disable=E1101

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.avatar and settings.DEFAULT_PROFILE:
            result = urlretrieve(settings.DEFAULT_PROFILE)
            self.avatar.save(  # pylint: disable=E1101
                "default-avatar.png", File(open(result[0], "rb"))
            )
        img_path = self.avatar.path  # pylint: disable=E1101
        if self.user.is_superuser and settings.ADMIN_PROFILE:
            os.remove(img_path)
            result = urlretrieve(settings.ADMIN_PROFILE)
            img_path = result[0]
        img = Image.open(img_path)
        if img.height > 250 or img.width > 250:
            img.thumbnail((250, 250))
        self.avatar.name = f"profile/{self.pk}-avatar.png"
        avatar_path = self.avatar.path  # pylint: disable=E1101
        img.save(avatar_path, bitmap_format="png")
        if not img_path == avatar_path:
            os.remove(img_path)
