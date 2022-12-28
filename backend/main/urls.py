"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import annotations

import oauth2_provider.views as oauth2_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import URLPattern, URLResolver, include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

oauth2_endpoint_views = []

# OAuth2 Application Management endpoints
oauth2_endpoint_views += [
    path("applications/", oauth2_views.ApplicationList.as_view(), name="list"),
    path(
        "applications/register/",
        oauth2_views.ApplicationRegistration.as_view(),
        name="register",
    ),
    path(
        "applications/<pk>/",
        oauth2_views.ApplicationDetail.as_view(),
        name="detail",
    ),
    path(
        "applications/<pk>/delete/",
        oauth2_views.ApplicationDelete.as_view(),
        name="delete",
    ),
    path(
        "applications/<pk>/update/",
        oauth2_views.ApplicationUpdate.as_view(),
        name="update",
    ),
]

# OAuth2 Token Management endpoints
oauth2_endpoint_views += [
    path(
        "authorized-tokens/",
        oauth2_views.AuthorizedTokensListView.as_view(),
        name="authorized-token-list",
    ),
    path(
        "authorized-tokens/<pk>/delete/",
        oauth2_views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete",
    ),
]


urlpatterns: list[URLResolver | URLPattern] = [
    path("", include("pwa.urls")),
    path("", lambda request: redirect("home/")),
    path("", include("scheduler.urls")),
    path(
        "admin/oauth/",
        include(
            (oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider"
        ),
    ),
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
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
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
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
