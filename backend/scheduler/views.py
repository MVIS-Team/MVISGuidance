from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, cast

import scheduler
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
from scheduler.forms import SessionForm
from scheduler.models import Session

if TYPE_CHECKING:
    from typing import Literal, Sequence, Type

    from django.contrib.auth.models import User as _User

User: Type[_User] = cast("Type[_User]", auth.get_user_model())

timeblock = {
        "A": "8:30-9:00",
        "B": "9:00-9:30",
        "C": "9:30-10:00",
        "D": "10:00-10:30",
        "E": "10:30-11:00",
        "F": "11:00-11:30",
        "G": "11:30-12:00",
        "H": "12:00-12:30",
        "I": "12:30-13:00",
        "J": "13:00-13:30",
        "K": "13:30-14:00",
        "L": "14:00-14:30",
        "M": "14:30-15:00",
        "N": "15:00-15:30",
        "O": "15:30-16:00",
        "P": "16:00-16:30",
}

suffix = "\n\nMVIS ยินดีอย่างยิ่งที่ได้รับใช้ท่าน\nอย่าลืมนัดนะง้าบบบ"
ggMeetLink = []
onlineMeet = '\nโปรดมาพบกันที่มีท https://meet.google.com/kpz-mciv-xes'

# Create your views here.
def generate_daylist(student, teacher):
    if not teacher:
        return {}
    daylist = []
    today = datetime.date.today()
    for i in range(7):
        day = {}
        curr_day = today + datetime.timedelta(days=i)
        weekday = curr_day.strftime("%A").upper()
        day["date"] = str(curr_day)
        day["day"] = weekday
        day["onduty"] = teacher
        day["dept"] = ""
        day["booked"] = {}
        for (key, time) in Session.TIMEBLOCK_CHOICES:
            day["booked"][key] = (
                time,
                Session.objects.filter(
                    Q(date=str(curr_day))
                    & Q(timeblock=key)
                    & (Q(teacher=teacher) | Q(student=student))
                ).exists(),
            )
        daylist.append(day)
    return daylist


class SessionCreateView(LoginRequiredMixin, CreateView):
    form_class = SessionForm
    template_name = "scheduler/session_form.html"

    def get_initial(self):
        return {
            "date": self.kwargs.get("date"),
            "timeblock": self.kwargs.get("timeblock"),
            "teacher": User.objects.get(pk=self.kwargs.get("teacher_pk")),
            "student": self.request.user,
        }

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_success_url(self):
        user: _User = self.request.user  # type: ignore
        pk = self.kwargs.get('teacher_pk') 
        content = f'เรียนคุณ { self.request.user } และอาจารย์ { auth.get_user_model().objects.get(id = pk) }\n\n'
        content += f'เรามีนัดคุยกันในหัวข้อ { self.request.POST.get("topic") } ใน{ self.kwargs.get("date").strftime("วันที่ %d เดือน %m ปี %Y") } ช่วง { timeblock[self.kwargs.get("timeblock")] }'
        if self.request.POST.get('location') == 'online':
           content += onlineMeet
        content += suffix
        send_mail('จองเวลาคุยกับอาจารย์', content, 'mvisguidance@gmail.com',[self.request.user.email, auth.get_user_model().objects.get(id = pk).email])
        return reverse("users:detail", args=[user.username])


class SessionEditView(
    SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    model = Session
    success_message = "Session was updated successfully"
    permission_required = "scheduler.change_session"
    fields: Literal["__all__"] | Sequence[str] = ["location"]

    def get_success_url(self):
        user: _User = self.request.user  # type: ignore
        pk = self.kwargs.get('pk')
        content = f'เรียนคุณ { self.request.user } และอาจารย์ { auth.get_user_model().objects.get(id = scheduler.models.Session.objects.get(id=pk).teacher_id) }\n\n'
        content += f'เราขอเปลี่ยนแปลงการนัดใน{ scheduler.models.Session.objects.get(id=pk).date.strftime(f"วันที่ %d เดือน %B ปี %Y") } ช่วง { timeblock[scheduler.models.Session.objects.get(id=pk).timeblock] } ให้เป็นแบบ { scheduler.models.Session.objects.get(id=pk).location }'
        if scheduler.models.Session.objects.get(id=pk).location == 'online':
            content += onlineMeet 
        content += suffix
        send_mail('เปลี่ยนแปลงการนัด', content, 'mvisguidance@gmail.com',[self.request.user.email, auth.get_user_model().objects.get(id = scheduler.models.Session.objects.get(id=pk).teacher_id).email]) 
        return reverse("users:detail", args=[user.username])


class SessionCancelView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Session
    permission_required = "scheduler.delete_session"

    def get_success_url(self):
        user: _User = self.request.user  # type: ignore
        pk = self.kwargs.get('pk')
        content = f'เรียนคุณ { self.request.user } และอาจารย์ { auth.get_user_model().objects.get(id = scheduler.models.Session.objects.get(id=pk).teacher_id) }\n\n'
        content += f'ขออภัยเป็นอย่างยิ่ง เราขอยกเลิกนัดใน{ scheduler.models.Session.objects.get(id=pk).date.strftime(f"วันที่ %d เดือน %B ปี %Y") } ช่วง { timeblock[scheduler.models.Session.objects.get(id=pk).timeblock] } เนื่องจากมีสมาชิกไม่สะดวก กรุณานัดเวลาใหม่ในระบบอีกครั้ง'
        content += suffix
        send_mail('ขอยกเลิกนัด', content, 'mvisguidance@gmail.com', [self.request.user.email, auth.get_user_model().objects.get(id = scheduler.models.Session.objects.get(id=pk).teacher_id).email])
        return reverse("users:detail", args=[user.username])


def book(request, teacher_pk):
    if request.user.is_authenticated:
        student = request.user
        teacher = User.objects.get(pk=teacher_pk)
        if not teacher:
            raise ValidationError(_("Teacher does not exist."), code="invalid")
        if not teacher.groups.filter(name="teacher"):
            raise ValidationError(
                _("Teacher is not actually a teacher."), code="invalid"
            )
        context = {
            "days": generate_daylist(student, teacher),
            "teacher": teacher,
        }
        return render(request, "pages/booking.html", context)
    else:
        return redirect("/accounts/login/")


def sessions(request):
    context = {"sessions": Session.objects.all()}
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
    return render(request, "pages/teachers.html", context)

def teacherSchedule(request):
    context ={}
    return render(request, "pages/forTeacher.html", context)
