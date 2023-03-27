from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import path

from users import views

app_name = "users"
urlpatterns = [
    path(
        "~redirect/",
        name="redirect",
        view=views.profile_redirect_view,
    ),
    path(
        "~redirect/<str:username>/",
        name="redirect",
        view=views.profile_redirect_view,
    ),
    path(
        "~update/",
        name="update",
        view=views.profile_update_view,
    ),
    path(
        "<str:username>/",
        name="detail",
        view=views.profile_detail_view,
    ),
    path(
        "login/",
        name="login",
        view=auth_views.LoginView.as_view(template_name="users/login.html"),
    ),
    path(
        "logout/",
        name="logout",
        view=auth_views.LogoutView.as_view(template_name="users/logout.html"),
    ),
]
