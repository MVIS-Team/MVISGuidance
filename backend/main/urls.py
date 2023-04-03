from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import URLPattern, URLResolver, include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns: list[URLResolver | URLPattern] = [
    path("", include("pwa.urls")),
    path("", lambda request: redirect("home/")),
    path("", include("scheduler.urls")),
    path("admin/", admin.site.urls),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    path("users/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar.urls

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
