from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import path
from users import views

app_name = "users"
urlpatterns = [
    path("~redirect/", view=views.profile_redirect_view, name="redirect"),
    path(
        "~redirect/<str:username>/", view=views.profile_redirect_view, name="redirect"
    ),
    path("~update/", view=views.profile_update_view, name="update"),
    path("<str:username>/", view=views.profile_detail_view, name="detail"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
]
