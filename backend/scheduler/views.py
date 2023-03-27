from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, cast

from django.contrib import auth
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, UpdateView
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin

from scheduler.forms import SessionForm, TeacherSessionForm
from scheduler.models import Session

if TYPE_CHECKING:
    from typing import Any, Optional, Type

    from django.contrib.auth.models import AbstractUser

User: Type[AbstractUser] = cast("Type[AbstractUser]", auth.get_user_model())


def generate_daylist(student: AbstractUser, teacher: AbstractUser):
    if not teacher:
        return {}
    daylist = []
    earliest_book_time = datetime.datetime.now() + datetime.timedelta(hours=12)
    startday = datetime.date.today()
    if startday.weekday() > 4:
        startday += datetime.timedelta(days=7 - startday.weekday())
    for i in range(5 - startday.weekday()):
        day: dict[str, Any] = {}
        curr_day = startday + datetime.timedelta(days=i)
        weekday = curr_day.strftime("%A").upper()
        day["date"] = str(curr_day)
        day["day"] = weekday
        day["onduty"] = teacher
        day["dept"] = ""
        day["booked"] = {}
        for key, time in Session.TIMEBLOCK_CHOICES:
            day["booked"][key] = (
                time,
                Session.objects.filter(
                    Q(date=str(curr_day))
                    & Q(timeblock=key)
                    & (Q(teacher=teacher) | Q(student=student))
                ).exists(),
            )
        for key, time in Session.TIMEBLOCK_CHOICES:
            start_time = datetime.datetime.strptime(
                curr_day.strftime("%d/%m/%Y") + " " + time.split("-", maxsplit=1)[0],
                "%d/%m/%Y %H:%M",
            )
            if start_time < earliest_book_time:
                day["booked"][i] = (time, True)

        daylist.append(day)
    return daylist


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
        timeblock = Session.TIMEBLOCK_CHOICES[session.timeblock]
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
            "mvisguidance@gmail.com",
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
        timeblock = Session.TIMEBLOCK_CHOICES[session.timeblock]
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
            "mvisguidance@gmail.com",
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
        timeblock = Session.TIMEBLOCK_CHOICES[session.timeblock]
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
            "mvisguidance@gmail.com",
            [session.student.email, session.teacher.email],
        )


class TeacherSchedule(LoginRequiredMixin, CreateView):
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


def book(request, teacher_pk):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    student = request.user
    teacher = User.objects.get(pk=teacher_pk)
    if not teacher:
        raise ValidationError(_("Teacher does not exist."), code="invalid")
    if not teacher.groups.filter(name="teacher"):
        raise ValidationError(_("Teacher is not actually a teacher."), code="invalid")
    context = {
        "days": generate_daylist(student, teacher),
        "teacher": teacher,
    }
    return render(request, "pages/booking.html", context)


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
    return render(request, "pages/teachers.html", context)


def teachertable(request):
    student = request.user
    teacher = User.objects.get(pk=request.user.id)
    curr_day = datetime.date.today()
    weekday = curr_day.strftime("%A").upper()
    day_list = [
        {
            "date": curr_day,
            "day": weekday,
            "onduty": teacher,
        }
    ]
    for i in generate_daylist(student, teacher):
        new_dict = {key: i[key] for key in ["date", "day", "onduty"]}
        day_list.append(new_dict)
    context = {
        "days": day_list,
        "teacher": teacher,
    }
    return render(request, "pages/teachertable.html", context)
