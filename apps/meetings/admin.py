from django.contrib import admin
from .models import Meeting, MeetingSchedule


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'created_time', 'updated_time')


@admin.register(MeetingSchedule)
class MeetingScheduleAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'available_at', 'is_active')
