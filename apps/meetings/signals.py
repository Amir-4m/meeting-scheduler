from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ReservedMeeting, MeetingSchedule


@receiver(post_save, sender=ReservedMeeting)
def reserved_meeting_post_save(sender, instance, created, **kwargs):
    if created:
        MeetingSchedule.objects.filter(id=instance.meeting_schedule.id).update(is_reserved=True)
