from __future__ import annotations

from datetime import datetime

from django.urls import path, register_converter

from scheduler import views


class DateConverter:
    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d")

    def to_url(self, value):
        return value


register_converter(DateConverter, "yyyy")

urlpatterns = [
    path(
        "home/",
        name="scheduler-home",
        view=views.home,
    ),
    path(
        "book/<int:teacher_pk>",
        name="scheduler-book",
        view=views.book,
    ),
    path(
        "sessions/new/<int:teacher_pk>/<yyyy:date>/<str:timeblock>",
        name="session-create-spec",
        view=views.SessionCreateView.as_view(),
    ),
    path(
        "sessions/<int:pk>/edit",
        name="session-edit",
        view=views.SessionEditView.as_view(),
    ),
    path(
        "sessions/<int:pk>/cancel",
        name="session-cancel",
        view=views.SessionCancelView.as_view(),
    ),
    path(
        "teacherSchedule/",
        name="teachertable",
        view=views.teachertable,
    ),
    path(
        "sessions/new/teacherSchedule/<int:teacher_pk>/<yyyy:date>/<str:timeblock>",
        name="teacherSchedule",
        view=views.TeacherSchedule.as_view(),
    ),
]
