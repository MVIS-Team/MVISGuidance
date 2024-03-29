from __future__ import annotations

import csv
import datetime
import io
from typing import TYPE_CHECKING, cast

from django.contrib import auth
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, UpdateView
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from guardian.shortcuts import get_objects_for_user

from scheduler.forms import SessionForm, TeacherSessionForm
from scheduler.models import Session

if TYPE_CHECKING:
    from typing import Any, Optional, Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


def generate_week_data(student: AbstractUser, teacher: AbstractUser, week: int = 0):
    if not teacher:
        return []
    is_self = student.pk == teacher.pk
    data_week = []
    now = datetime.datetime.now()
    earliest_book_time = (
        now + datetime.timedelta(hours=1)
        if is_self
        else now + datetime.timedelta(hours=12)
    )
    latest_book_time = (
        datetime.datetime.max if is_self else now + datetime.timedelta(weeks=1)
    )
    startday = now.date() + datetime.timedelta(
        weeks=week + (1 if now.weekday() > 5 else 0), days=-now.weekday()
    )
    for i in range(5):
        data_day: dict[str, Any] = {}
        curr_day = startday + datetime.timedelta(days=i)
        weekday = curr_day.strftime("%A").upper()
        data_day["date"] = str(curr_day)
        data_day["weekday"] = weekday
        data_day["timeblocks"] = {}
        for key, time in Session.TIMEBLOCK_CHOICES:
            start_time = datetime.datetime.strptime(
                curr_day.strftime("%d/%m/%Y") + " " + time.split("-", maxsplit=1)[0],
                "%d/%m/%Y %H:%M",
            )
            end_time = datetime.datetime.strptime(
                curr_day.strftime("%d/%m/%Y") + " " + time.split("-", maxsplit=1)[1],
                "%d/%m/%Y %H:%M",
            )
            is_past = start_time <= earliest_book_time
            is_future = latest_book_time <= end_time
            try:
                is_booked = Session.objects.get(
                    Q(date=str(curr_day)) & Q(timeblock=key) & Q(student=student)
                )
            except Session.DoesNotExist:
                is_booked = None
            try:
                is_full = Session.objects.get(
                    Q(date=str(curr_day)) & Q(timeblock=key) & Q(teacher=teacher)
                )
            except Session.DoesNotExist:
                is_full = None
            data_day["timeblocks"][key] = {
                "label": time,
                "is_avaliable": not (is_past or is_future or is_booked or is_full),
                "session": is_full if is_self else is_booked,
            }
        if is_self:
            data_day["timeblocks_teacher"] = {}
            timeblocks = dict(Session.TIMEBLOCK_CHOICES)
            for key, text, time_keys in Session.TEACHER_TIMEBLOCK:
                start_time = datetime.datetime.strptime(
                    curr_day.strftime("%d/%m/%Y")
                    + " "
                    + timeblocks[time_keys[0]].split("-", maxsplit=1)[0],
                    "%d/%m/%Y %H:%M",
                )
                end_time = datetime.datetime.strptime(
                    curr_day.strftime("%d/%m/%Y")
                    + " "
                    + timeblocks[time_keys[-1]].split("-", maxsplit=1)[1],
                    "%d/%m/%Y %H:%M",
                )
                is_past = start_time <= earliest_book_time
                is_future = latest_book_time <= end_time
                is_booked = Session.objects.filter(
                    Q(date=str(curr_day))
                    & Q(timeblock__in=time_keys)
                    & Q(teacher=teacher)
                    & ~Q(student=student)
                ).exists()
                data_day["timeblocks_teacher"][key] = {
                    "label": text,
                    "is_avaliable": not (is_past or is_future or is_booked),
                }

        data_week.append(data_day)
    return data_week


def send_session_create_mail(
    session: Session,
    topic: Optional[str],
):
    if session.student != session.teacher:
        date = (
            session.date.strftime(
                "วันที่ %d เดือน %B ปี %Y".encode("unicode-escape").decode()
            )
            .encode()
            .decode("unicode-escape")
        )
        timeblock = dict(Session.TIMEBLOCK_CHOICES)[session.timeblock]  # type: ignore
        meet_url = f"https://meet.google.com/lookup/{session.teacher.username}"
        send_mail(
            "จองเวลาคุยกับอาจารย์",
            (
                f"เรียนคุณ { session.student.username } และอาจารย์ { session.teacher.username }"
                "\n\n"
                f"เรามีนัดคุยกัน"
                f'{f"ในหัวข้อ { topic } " if topic else ""}'
                f"ใน { date } ช่วง { timeblock } "
                f'{f"โปรดมาพบกันที่มีท {meet_url}" if session.location == "online" else ""}'
                "\n\n"
                "MVIS ยินดีอย่างยิ่งที่ได้รับใช้ท่าน"
                "\n"
                "อย่าลืมนัดนะง้าบบบ"
            ),
            None,
            [session.student.email, session.teacher.email],
        )


def send_session_edit_mail(
    session: Session,
):
    if session.student != session.teacher:
        date = (
            session.date.strftime(
                "วันที่ %d เดือน %B ปี %Y".encode("unicode-escape").decode()
            )
            .encode()
            .decode("unicode-escape")
        )
        timeblock = dict(Session.TIMEBLOCK_CHOICES)[session.timeblock]  # type: ignore
        meet_url = f"https://meet.google.com/lookup/{session.teacher.username}"
        send_mail(
            "ขอยกเลิกนัด",
            (
                f"เรียนคุณ { session.student.username } และอาจารย์ { session.teacher.username }"
                "\n\n"
                "เราขอเปลี่ยนแปลงการนัด"
                f"ใน { date } ช่วง { timeblock } "
                f"ให้เป็นแบบ { session.location } "
                f'{f"โปรดมาพบกันที่มีท {meet_url}" if session.location == "online" else ""}'
                "\n\n"
                "MVIS ยินดีอย่างยิ่งที่ได้รับใช้ท่าน"
                "\n"
                "อย่าลืมนัดนะง้าบบบ"
            ),
            None,
            [session.student.email, session.teacher.email],
        )


def send_session_cancel_mail(
    requested: AbstractUser,
    session: Session,
):
    if session.student != session.teacher:
        date = (
            session.date.strftime(
                "วันที่ %d เดือน %B ปี %Y".encode("unicode-escape").decode()
            )
            .encode()
            .decode("unicode-escape")
        )
        timeblock = dict(Session.TIMEBLOCK_CHOICES)[session.timeblock]  # type: ignore
        send_mail(
            "ขอยกเลิกนัด",
            (
                f"เรียนคุณ { session.student.username } และอาจารย์ { session.teacher.username }"
                "\n\n"
                "ขออภัยเป็นอย่างยิ่ง เราขอยกเลิกนัด"
                f"ใน { date } ช่วง { timeblock } "
                f"เนื่องจากคุณ { requested } ไม่สะดวก "
                "กรุณานัดเวลาใหม่ในระบบอีกครั้ง"
                "\n\n"
                "MVIS ยินดีอย่างยิ่งที่ได้รับใช้ท่าน"
                "\n"
                "อย่าลืมนัดนะง้าบบบ"
            ),
            None,
            [session.student.email, session.teacher.email],
        )


class SessionCreateView(LoginRequiredMixin, CreateView):
    form_class = SessionForm
    template_name = "scheduler/session_form.html"

    def get_initial(self):
        return {
            "date": self.kwargs.get("date"),
            "timeblock": self.kwargs.get("timeblock"),
            "teacher": User.objects.get(pk=self.kwargs.get("teacher_pk")),
            "student": self.request.user,
            "location": self.kwargs.get("location"),
            "topic": self.kwargs.get("topic"),
        }

    def get_success_url(self):
        user = cast("User", self.request.user)
        session = cast("Session", self.object)  # type:ignore
        send_session_create_mail(session, self.request.POST.get("topic"))
        return reverse("users:detail", args=[user.username])


class SessionEditView(
    SuccessMessageMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = Session
    success_message = "Session was updated successfully"
    permission_required = "scheduler.change_session"
    fields = ("location",)

    def get_success_url(self):
        session_id = self.kwargs.get("pk")
        session = Session.objects.get(id=session_id)
        user = cast("User", self.request.user)
        send_session_edit_mail(session)
        return reverse("users:detail", args=[user.username])


class SessionCancelView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Session
    permission_required = "scheduler.delete_session"

    def get_success_url(self):
        session_id = self.kwargs.get("pk")
        session = Session.objects.get(id=session_id)
        user = cast("User", self.request.user)
        send_session_cancel_mail(user, session)
        return reverse("users:detail", args=[user.username])


def book(request, teacher_pk, week=0):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    student = request.user
    teacher = User.objects.get(pk=teacher_pk)
    if not teacher:
        raise ValidationError(_("Teacher does not exist."), code="invalid")
    if not teacher.groups.filter(name="teacher"):
        raise ValidationError(_("Teacher is not actually a teacher."), code="invalid")
    context = {
        "week": generate_week_data(student, teacher, week),
        "teacher": teacher,
        "prev_week": week - 1,
        "next_week": week + 1,
    }
    return render(request, "scheduler/booking.html", context)


def sessions_list(request):
    profile = request.user.profile
    user = request.user
    sessions = get_objects_for_user(
        user, "scheduler.view_session", with_superuser=False
    )
    context = {
        "user": user,
        "teacher_sessions": sessions.filter(teacher=profile.user),
        "student_sessions": sessions.filter(student=profile.user),
        "sessions": sessions,
    }
    return render(request, "scheduler/sessions.html", context)


def home(request):
    teachers = User.objects.filter(groups__name="teacher")
    context = {
        "teachers": [
            {
                "profile": teacher.profile,  # type: ignore
                "pk": teacher.pk,
            }
            for teacher in teachers
        ]
    }
    return render(request, "scheduler/teachers.html", context)


class Teacher:
    @classmethod
    def export(cls, request):
        user = request.user
        sessions = get_objects_for_user(
            user, "scheduler.view_session", with_superuser=False
        ).filter(teacher=user, date__lt=datetime.date.today())
        content = (
            f"เรียนอาจารย์ { user.username }"
            "\n\n"
            f"ตามที่ท่านได้ขอข้อมูลการจองในอดีตไว้ เราขอส่งข้อมูลนั้นให้กับท่าน"
            "\n\n"
            "MVIS ยินดีอย่างยิ่งที่ได้รับใช้ท่าน"
            "\n"
            "อย่าลืมนัดนะง้าบบบ"
        )
        email = EmailMessage(
            "สรุปข้อมูล",
            content,
            None,
            [user.email],
        )
        csvfile = io.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["student", "teacher", "date", "timeblock", "location"])
        for session in sessions:
            print(session.is_upcoming())
            csvwriter.writerow(
                [
                    session.student.username,
                    session.teacher.username,
                    session.date.strftime("%d/%m/%Y"),
                    dict(Session.TIMEBLOCK_CHOICES)[session.timeblock],
                    session.location,
                ]
            )
        email.attach("data.csv", csvfile.getvalue(), "text/csv")
        email.send()
        return redirect("/")

    class TeacherSessionCreateView(LoginRequiredMixin, CreateView):
        form_class = TeacherSessionForm
        template_name = "scheduler/session_form.html"

        def get_initial(self):
            return {
                "date": self.kwargs.get("date"),
                "timeblock": self.kwargs.get("timeblock"),
                "teacher": User.objects.get(pk=self.kwargs.get("teacher_pk")),
                "student": self.request.user,
            }

        def get_success_url(self):
            teacher_id = self.kwargs.get("teacher_pk")
            user = cast("AbstractUser", self.request.user)
            day = self.kwargs.get("date")
            time_list = {
                "allday": [chr(i) for i in range(65, 81)],
                "allam": [chr(i) for i in range(65, 72)],
                "allpm": [chr(i) for i in range(74, 81)],
            }[self.kwargs.get("timeblock")]
            sessions = Session.objects.filter(
                date=day,
                teacher_id=teacher_id,
                timeblock__in=time_list,
            )
            for session in sessions:
                send_session_cancel_mail(user, session)
            sessions.delete()

            for timeblock in time_list:
                session = Session(
                    student_id=teacher_id,
                    teacher_id=teacher_id,
                    date=day,
                    timeblock=timeblock,
                    location="onsite",
                )
                session.save()

            return reverse("users:detail", args=[user.username])
