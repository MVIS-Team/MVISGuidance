from __future__ import annotations

from typing import TYPE_CHECKING, cast

from allauth.account.forms import SignupForm
from django import forms
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.utils.translation import gettext_lazy as _

from users.models import Profile

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


class SignupFormCustom(SignupForm):
    first_name = forms.CharField(label=_("First Name"), max_length=100)
    last_name = forms.CharField(label=_("Last Name"), max_length=100)
    avatar = forms.ImageField(label=_("Profile Image"), required=False)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.profile.avatar = self.cleaned_data.get("avatar")
        return user

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not hasattr(avatar, "content_type"):
            return avatar
        # validate content type
        main, sub = avatar.content_type.split("/")
        if not (main == "image" and sub in ["jpeg", "pjpeg", "gif", "png"]):
            raise forms.ValidationError("Please use a JPEG, GIF or PNG image.")
        return avatar


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
    avatar = forms.ImageField(label=_("Profile Image"), required=False)

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
        profile = super().save(*args, **kwargs)
        profile.user.first_name = self.cleaned_data.get("first_name")
        profile.user.last_name = self.cleaned_data.get("last_name")
        profile.user.avatar = self.cleaned_data.get("avatar")
        profile.user.save()
        return profile

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not hasattr(avatar, "content_type"):
            return avatar
        # validate content type
        main, sub = avatar.content_type.split("/")
        if not (main == "image" and sub in ["jpeg", "pjpeg", "gif", "png"]):
            raise forms.ValidationError("Please use a JPEG, GIF or PNG image.")
        return avatar
