from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from utils.base_models import TimeMixin


class Meeting(TimeMixin):
    INTERVAL_MINUTE_15 = 15
    INTERVAL_MINUTE_30 = 30
    INTERVAL_MINUTE_45 = 45
    INTERVAL_CHOICES = (
        (INTERVAL_MINUTE_15, _("15 Minutes")),
        (INTERVAL_MINUTE_30, _("30 Minutes")),
        (INTERVAL_MINUTE_45, _("45 Minutes"))

    )

    user = models.ForeignKey(User, verbose_name=_("Host"), related_name='meetings', on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=256, blank=True)
    description = models.TextField(_("Description"), blank=True)
    interval = models.PositiveSmallIntegerField(_("Interval"), choices=INTERVAL_CHOICES, default=INTERVAL_MINUTE_30)

    def __str__(self):
        return f'{self.title} - {self.user.username}'


class MeetingSchedule(TimeMixin):
    available_at = models.DateTimeField(_("Available at"))
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='schedules')
    is_active = models.BooleanField(_("Active ?"), default=True)
    is_reserved = models.BooleanField(_("Reserved ?"), default=False)

    class Meta:
        unique_together = ('available_at', 'meeting')

    def __str__(self):
        return f'{self.meeting.title} - {self.available_at}'


class ReservedMeeting(TimeMixin):
    guest_fullname = models.CharField(_("Guest fullname"), max_length=256)
    guest_email = models.EmailField(_("Guest email"))
    meeting_schedule = models.OneToOneField(MeetingSchedule, on_delete=models.PROTECT, related_name='reserved')

    def __str__(self):
        return f'{self.guest_fullname} - {self.guest_email} - {self.meeting_schedule.meeting.title}'
