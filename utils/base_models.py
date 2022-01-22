from django.utils.translation import ugettext_lazy as _
from django.db import models


class TimeMixin(models.Model):
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("updated time"), auto_now=True)

    class Meta:
        abstract = True
