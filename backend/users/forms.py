from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django import forms
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.utils.translation import gettext_lazy as _

from users.models import Profile

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta(auth_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta(auth_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "name": {"unique": _("This username has already been taken.")}
        }


class ProfileChangeForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"), max_length=100)
    last_name = forms.CharField(label=_("Last Name"), max_length=100)

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "avatar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.order_fields(["first_name", "last_name", self.field_order])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.user.first_name = self.cleaned_data.get("first_name")
        self.instance.user.last_name = self.cleaned_data.get("last_name")
        self.instance.user.save()

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar
        # validate content type
        main, sub = avatar.content_type.split("/")
        if not (main == "image" and sub in ["jpeg", "pjpeg", "gif", "png"]):
            raise forms.ValidationError("Please use a JPEG, GIF or PNG image.")
        # validate file size
        if len(avatar) > (20 * 1024):
            raise forms.ValidationError("Avatar file size may not exceed 20k.")

        return avatar
