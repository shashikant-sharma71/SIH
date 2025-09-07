from django.contrib import admin
from .models import Student, Faculty, Subject, AttendanceRecord

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'get_username', 'roll_no', 'course')
    search_fields = ('roll_no', 'first_name', 'last_name')
    list_filter = ('course',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'email')  # Adjust fields accordingly

    def get_username(self, obj):
        return obj.username  # Use 'name' or whatever field your Faculty model actually has
    get_username.short_description = 'Name'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_code', 'short_name', 'faculty')
    search_fields = ('course_name',)

@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'present')
    list_filter = ('subject', 'date', 'present')
    search_fields = ('student__roll_no', 'subject__course_name')
    date_hierarchy = 'date'