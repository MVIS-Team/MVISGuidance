from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Issue(models.Model):
    email: models.EmailField = models.EmailField()
    issue: models.TextField = models.TextField()
    user_agent: models.CharField = models.CharField(max_length=200)
    date_posted: models.DateTimeField = models.DateTimeField(default=timezone.now)

    # dunder STR
    def __str__(self):
        return self.email
