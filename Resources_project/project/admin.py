from django.contrib import admin
from .models import Department, ICTFacility, LibraryResource, UserProfile, Teacher, EContentDevelopment

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'department_name')
    search_fields = ('department_name',)

@admin.register(ICTFacility)
class ICTFacilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'room_type', 'room_no', 'ict_facility')
    list_filter = ('department', 'room_type')
    search_fields = ('room_no', 'ict_facility')

@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_year', 'resource_name', 'total_expenditure', 'department')
    list_filter = ('academic_year', 'department')
    search_fields = ('resource_name', 'academic_year')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    list_filter = ('department',)
    search_fields = ('user__username',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_department', 'position')
    list_filter = ('user_profile__department', 'position')
    search_fields = ('user_profile__user__username', 'user_profile__department__department_name')
    ordering = ('user_profile__user__username',)

    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = "Username"

    def get_department(self, obj):
        return obj.user_profile.department.department_name if obj.user_profile.department else "No Department"
    get_department.short_description = "Department"

@admin.register(EContentDevelopment)
class EContentDevelopmentAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'teacher', 'platform', 'launch_date')
    list_filter = ('platform', 'launch_date')
    search_fields = ('module_name', 'teacher__user_profile__user__username')
