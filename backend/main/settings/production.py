from __future__ import annotations

import os

from decouple import config

from main.settings.base import *  # noqa # pylint: disable=W0401,W0614

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [config("DJANGO_HOSTNAME", default="*")]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join("/var/www/MVISGuidance/", "static")

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join("/var/www/MVISGuidance/", "media")


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = config("DJANGO_SECURE_SSL_REDIRECT", default=True, cast=bool)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_SECONDS = 518400  # Set this to 60 seconds first and then to 518400 once you prove the former works
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = config("DJANGO_SECURE_HSTS_PRELOAD", default=True, cast=bool)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = config(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
)

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = config("EMAIL_HOST", default="")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = config("EMAIL_PORT", default="587", cast=int)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-use-lts
EMAIL_USE_TLS = True

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
LOGGING["filters"] = {  # noqa
    "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
}
LOGGING["handlers"]["mail_admins"] = {  # type: ignore # noqa
    "level": "ERROR",
    "filters": ["require_debug_false"],
    "class": "django.utils.log.AdminEmailHandler",
}
LOGGING["loggers"] = {  # noqa
    "django.request": {
        "handlers": ["mail_admins"],
        "level": "ERROR",
        "propagate": True,
    },
    "django.security.DisallowedHost": {
        "level": "ERROR",
        "handlers": ["console", "mail_admins"],
        "propagate": True,
    },
}

# django pwa
# ------------------------------------------------------------------------------
PWA_APP_DEBUG_MODE = False
