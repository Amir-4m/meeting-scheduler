from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from apps.meetings.models import Meeting, MeetingSchedule, ReservedMeeting


class ScheduleSerializer(WritableNestedModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = ('id', 'available_at', 'is_active')


class MeetingSerializer(WritableNestedModelSerializer):
    schedules = ScheduleSerializer(many=True, required=False)

    class Meta:
        model = Meeting
        exclude = ('user',)


class ReservedMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedMeeting
        fields = '__all__'

    def validate(self, attrs):
        meeting_schedule = attrs['meeting_schedule']
        if not meeting_schedule.is_active:
            raise ValidationError({'meeting_schedule': _("this schedule is not active")})
        return super(ReservedMeetingSerializer, self).validate(attrs)
