from django.contrib import admin
from .models import Meeting, MeetingSchedule, ReservedMeeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_time', 'updated_time')


@admin.register(MeetingSchedule)
class MeetingScheduleAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'available_at', 'is_active')


@admin.register(ReservedMeeting)
class ReservedMeetingAdmin(admin.ModelAdmin):
    list_display = ('guest_fullname', 'guest_email', 'meeting_schedule')
