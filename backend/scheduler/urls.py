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
    path("home/", views.home, name="scheduler-home"),
    path("book/<int:teacher_pk>", views.book, name="scheduler-book"),
    path(
        "sessions/new/<int:teacher_pk>/<yyyy:date>/<str:timeblock>",
        views.SessionCreateView.as_view(),
        name="session-create-spec",
    ),
    path(
        "sessions/<int:pk>/edit", views.SessionEditView.as_view(), name="session-edit"
    ),
    path(
        "sessions/<int:pk>/cancel",
        views.SessionCancelView.as_view(),
        name="session-cancel",
    ),
    path("teacherSchedule/", views.teacherSchedule, name='teacherSchedule')
]
