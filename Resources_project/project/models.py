import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# File size validation (Max 5MB)
def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError("File size should not exceed 5MB.")

# File type validation (PDF & Word only)
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext not in valid_extensions:
        raise ValidationError("Only PDF and Word documents (.pdf, .doc, .docx) are allowed.")

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class LibraryResource(models.Model):
    academic_year = models.CharField(max_length=9)
    resource_name = models.CharField(max_length=100)
    expenditure_journals = models.DecimalField(max_digits=10, decimal_places=2)
    expenditure_other_resources = models.DecimalField(max_digits=10, decimal_places=2)
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    document = models.FileField(
        upload_to='library_documents/',
        validators=[validate_file_size, validate_file_extension],
        blank=True,  # Allow empty files
        null=True    # Allow null values in the database
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.total_expenditure = self.expenditure_journals + self.expenditure_other_resources
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_year} - {self.resource_name} - {self.department.name}"


class UserProfile(models.Model):
    """Stores user department information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def is_library_user(self):
        """Check if user is part of the Library department."""
        return self.department and self.department.name.lower() == "library"

    def __str__(self):
        return f"{self.user.username} - {self.department.name if self.department else 'No Department'}"
