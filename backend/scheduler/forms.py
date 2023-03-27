from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django import forms
from django.contrib import auth

from scheduler.models import Session, TeacherSession

if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


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
        fields = (
            "student",
            "teacher",
            "date",
            "timeblock",
            "location",
            "topic",
        )


class TeacherSessionForm(forms.ModelForm):
    date = forms.DateField(disabled=True)
    timeblock = forms.CharField(disabled=True)
    teacher = forms.ModelChoiceField(User.objects.all(), disabled=True)
    student = forms.ModelChoiceField(User.objects.all(), disabled=True)

    class Meta:
        model = TeacherSession
        fields = (
            "student",
            "teacher",
            "date",
            "timeblock",
            # "location",
        )
