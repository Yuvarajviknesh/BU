import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# ✅ File size validation (Max 5MB)
def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError("File size should not exceed 5MB.")

# ✅ File type validation (PDF & Word only)
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext not in valid_extensions:
        raise ValidationError("Only PDF and Word documents (.pdf, .doc, .docx) are allowed.")

class Department(models.Model):
    department_code = models.CharField(max_length=10, primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.department_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def is_library_user(self):
        return self.department and self.department.department_name.lower() == "library"

    def __str__(self):
        return f"{self.user.username} - {self.department.department_name if self.department else 'No Department'}"

class Teacher(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)  # Linked to UserProfile
    position = models.CharField(max_length=100, choices=[
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('Researcher', 'Researcher'),
    ])

    def __str__(self):
        return f"{self.user_profile.user.username} ({self.position})"

class ICTFacility(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=100)
    room_no = models.CharField(max_length=20)
    ict_facility = models.TextField()
    geo_tagged_photo = models.ImageField(upload_to='ict_photos/', validators=[validate_file_size], blank=True, null=True)
    master_timetable = models.FileField(upload_to='timetables/', validators=[validate_file_size], blank=True, null=True)

    def __str__(self):
        return f"{self.department.department_name} - {self.room_type} ({self.room_no})"

class LibraryResource(models.Model):
    academic_year = models.CharField(max_length=9)
    resource_name = models.CharField(max_length=100)
    expenditure_journals = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expenditure_other_resources = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    document = models.FileField(upload_to='library_documents/', validators=[validate_file_size, validate_file_extension], blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.total_expenditure = (self.expenditure_journals or 0) + (self.expenditure_other_resources or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_year} - {self.resource_name} - {self.department.department_name}"

class EContentDevelopment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    module_name = models.CharField(max_length=200)
    platform = models.CharField(max_length=100)
    launch_date = models.DateField()
    document_link = models.FileField(upload_to='econtent_documents/', validators=[validate_file_size, validate_file_extension], null=True, blank=True)
    facility_available = models.TextField()
    video_link = models.URLField(help_text="Provide link to video.", null=True, blank=True)

    def __str__(self):
        return f"{self.module_name} by {self.teacher.user_profile.user.username}"

class Expenditure(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2)
    expenditure_infra = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenditure = models.DecimalField(max_digits=12, decimal_places=2)
    academic_facilities = models.DecimalField(max_digits=12, decimal_places=2)
    physical_facilities = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.department} - {self.year} - ₹{self.total_expenditure}"
