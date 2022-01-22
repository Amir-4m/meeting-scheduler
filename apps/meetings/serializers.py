from drf_writable_nested import WritableNestedModelSerializer

from apps.meetings.models import Meeting, MeetingSchedule


class ScheduleSerializer(WritableNestedModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = ('id', 'available_at', 'is_active')


class MeetingSerializer(WritableNestedModelSerializer):
    schedules = ScheduleSerializer(many=True, required=False)

    class Meta:
        model = Meeting
        exclude = ('user',)
