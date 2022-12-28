from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django import forms
from django.contrib import auth

from scheduler.models import Session

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import User as _User

User: Type[_User] = cast("Type[_User]", auth.get_user_model())


class SessionForm(forms.ModelForm):
    date = forms.DateField(disabled=True)
    timeblock = forms.CharField(
        widget=forms.Select(choices=Session.TIMEBLOCK_CHOICES), disabled=True
    )
    teacher = forms.ModelChoiceField(User.objects.all(), disabled=True)
    student = forms.ModelChoiceField(User.objects.all(), disabled=True)
    topic = forms.CharField(disabled=False)

    class Meta:
        model = Session
        exclude = ("date_posted",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
