from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, cast

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
if TYPE_CHECKING:
    from typing import Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


class Session(models.Model):
    TIMEBLOCK_CHOICES = (
        ("A", "8:30-9:00"),
        ("B", "9:00-9:30"),
        ("C", "9:30-10:00"),
        ("D", "10:00-10:30"),
        ("E", "10:30-11:00"),
        ("F", "11:00-11:30"),
        ("G", "11:30-12:00"),
        ("H", "12:00-12:30"),
        ("I", "12:30-13:00"),
        ("J", "13:00-13:30"),
        ("K", "13:30-14:00"),
        ("L", "14:00-14:30"),
        ("M", "14:30-15:00"),
        ("N", "15:00-15:30"),
        ("O", "15:30-16:00"),
        ("P", "16:00-16:30"),
    )
    LOCATION_CHOICES = (
        ("onsite", "Onsite"),
        ("online", "Online"),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_session",
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_session",
    )
    date_posted = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    timeblock = models.CharField(
        max_length=1,
        choices=TIMEBLOCK_CHOICES,
        default="A",
    )
    location = models.CharField(
        max_length=6,
        choices=LOCATION_CHOICES,
        default="onsite",
    )

    @property
    def time(self):
        return dict(self.TIMEBLOCK_CHOICES)[self.timeblock]  # type: ignore

    def validate_constraints(self, exclude=None):
        if exclude is None:
            exclude = []
        if "teacher" not in exclude:
            if not self.teacher.groups.filter(name="teacher").exists():
                raise ValidationError(
                    _("Teacher is not actually a teacher."), code="invalid"
                )
        if "date" not in exclude:
            if self.date is None:
                raise ValidationError("Wanna go on a date?")
            if not self.is_upcoming():
                raise ValidationError("You shall not book.")
        if "date_posted" not in exclude:
            # date_posted is forced to be datetime.now() via rest-api
            pass
            # if self.date_posted is None:
            #     raise ValidationError("What a great day, right?")
            # if self.date_posted != timezone.now():
            #     raise ValidationError("Back to the future?")
        if (
            "data" not in exclude
            and "timeblock" not in exclude
            and "location" not in exclude
        ):
            # onsite and online is not a restricted location
            pass
            # if (
            #     type(self)
            #     .objects.filter(
            #         Q(date=self.date)
            #         & Q(timeblock=self.timeblock)
            #         & Q(location=self.location)
            #     )
            #     .exists()
            # ):
            #     raise ValidationError("Oops, the room is not avaliable.")
        if (
            "data" not in exclude
            and "timeblock" not in exclude
            and "teacher" not in exclude
            and "student" not in exclude
        ):
            if (
                type(self)
                .objects.filter(
                    Q(date=self.date)
                    & Q(timeblock=self.timeblock)
                    & (
                        Q(teacher=self.teacher)
                        | Q(teacher=self.student)
                        | Q(student=self.teacher)
                        | Q(student=self.student)
                    )
                )
                .exists()
            ):
                raise ValidationError("Oops, somebody has already booked at this slot.")
        return super().validate_constraints(exclude=exclude)  # type: ignore

    # @property
    def is_upcoming(self):
        return date.today() <= self.date

    # is_upcoming.admin_order_field = "date"
    # is_upcoming.boolean = True
    # is_upcoming.short_description = "Session in the future?"

    @property
    def get_weekday(self):
        return self.date.strftime("%A")  # pylint: disable=E1101

    def __str__(self) -> str:
        return f"{self.date} {self.time} ({self.teacher.profile.name} {self.student.profile.name})"  # type: ignore

    def get_absolute_url(self):
        # returns a complete url string and let view handle the redirect
        return reverse("session-detail", kwargs={"pk": self.pk})


class TeacherSession(models.Model):
    student: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="studentSession",
    )
    teacher: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacherSession",
    )
    date: models.DateField = models.DateField(default=timezone.now)
    timeblock: models.CharField = models.CharField(max_length=6)

    class Meta:
        verbose_name = "Teacher Session"
        verbose_name_plural = "Teacher Sessions"
