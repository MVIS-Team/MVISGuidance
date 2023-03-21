from django.urls import path
from issue import views

urlpatterns = [
    path("", views.report_issues, name="scheduler-issues"),
]
