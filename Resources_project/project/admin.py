from django.contrib import admin
from .models import Department, LibraryResource, UserProfile

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_year', 'resource_name', 'total_expenditure', 'department')
    list_filter = ('department',)
    search_fields = ('resource_name', 'academic_year')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    list_filter = ('department',)
