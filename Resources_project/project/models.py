import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError("File size should not exceed 5MB.")

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
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True  # This enforces one profile per user
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_teacher = models.BooleanField(default=False)
    is_scholar = models.BooleanField(default=False)
    is_department_staff = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_profile'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.department.department_name if self.department else 'No Department'}"

class Teacher(models.Model):
    POSITION_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('Researcher', 'Researcher'),
    ]
    
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    pan = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.position}"

class OtpVerification(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at and not self.is_verified

    def __str__(self):
        return f"OTP for {self.email}"


class DemandRatio(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="demand_ratios")
    programme_name = models.CharField(max_length=255)
    programme_code = models.CharField(max_length=20)
    num_seats = models.PositiveIntegerField()
    num_applications = models.PositiveIntegerField()
    num_students_admitted = models.PositiveIntegerField()
    academic_year = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.programme_name} - {self.academic_year}"

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
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class TeacherAward(models.Model):
    RECOGNITION_LEVELS = [
        ('International', 'International'),
        ('National', 'National'),
        ('State', 'State'),
        ('Institutional', 'Institutional')
    ]

    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    award_name = models.CharField(max_length=255)
    recognition_level = models.CharField(max_length=50, choices=RECOGNITION_LEVELS)
    year_of_award = models.PositiveIntegerField()
    awarding_agency = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.teacher.user_profile.name} - {self.award_name} ({self.year_of_award})"
    
class GrantType(models.TextChoices):
    GOVERNMENT = 'Government', 'Government'
    NON_GOVERNMENT = 'Non-Government', 'Non-Government'

class DurationUnit(models.TextChoices):
    MONTHS = 'Months', 'Months'
    YEARS = 'Years', 'Years'

class ResearchGrant(models.Model):
    scheme_name = models.CharField(max_length=255)
    funding_agency = models.CharField(max_length=255)
    grant_type = models.CharField(max_length=20, choices=GrantType.choices)  # Renamed from "type"
    department = models.ForeignKey(Department, on_delete=models.CASCADE) 
    year_of_award = models.PositiveIntegerField()  # Ensures no negative values
    funds_provided = models.DecimalField(max_digits=15, decimal_places=2)  # Increased max_digits
    duration = models.PositiveIntegerField()  # Ensures no negative values
    duration_unit = models.CharField(max_length=10, choices=DurationUnit.choices)

    # Many-to-Many relationship for investigators
    investigators = models.ManyToManyField("Investigator", related_name="grants")

    def __str__(self):
        return f"{self.scheme_name} ({self.year_of_award})"

class Investigator(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensures unique names

    def __str__(self):
        return self.name
    
class AwardRecognition(models.Model):
    CATEGORY_CHOICES = [
        ('Institution', 'Institution'),
        ('Teacher', 'Teacher'),
        ('Research Scholar', 'Research Scholar'),
        ('Student', 'Student'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="awards")
    innovation_title = models.CharField(max_length=255)
    awardee_name = models.CharField(max_length=255)
    awarding_agency = models.CharField(max_length=255)
    award_year = models.PositiveIntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    document = models.FileField(
        upload_to='awards/', 
        validators=[validate_file_size, validate_file_extension], 
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"{self.innovation_title} - {self.awardee_name} ({self.award_year})"

class Patent(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="patents")
    patenter_name = models.CharField(max_length=255)
    patent_number = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    award_year = models.PositiveIntegerField()
    document = models.FileField(upload_to='patents/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.patent_number})"
    

class PhDAward(models.Model):
    scholar_name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="phds")
    guides = models.CharField(max_length=255)
    title = models.TextField()
    registration_year = models.PositiveIntegerField()
    award_year = models.PositiveIntegerField()
    document = models.FileField(upload_to='phdaward/', blank=True, null=True)

    def __str__(self):
        return f"{self.scholar_name} - {self.title} ({self.award_year})"
    
class ResearchPaper(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title of the Paper")
    authors = models.TextField(verbose_name="Name of the Author(s)")  # Supports multiple authors
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="research_papers",
        verbose_name="Department"
    )
    journal = models.CharField(max_length=255, verbose_name="Name of the Journal")
    year = models.PositiveIntegerField(verbose_name="Year of Publication")
    issn = models.CharField(max_length=15, verbose_name="ISSN Number")  # Adjust max_length for ISSN
    ugc_link = models.URLField(verbose_name="UGC Recognition Link", blank=True, null=True)
    document = models.FileField(upload_to='research_paper/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.authors} ({self.year})"
    
from django.db import models

class BookChapter(models.Model):
    teacher_name = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Name of the Teacher")
    book_title = models.CharField(max_length=255, verbose_name="Title of the Book/Chapter")
    paper_title = models.CharField(max_length=255, verbose_name="Title of the Paper", blank=True, null=True)
    proceedings_title = models.CharField(max_length=255, verbose_name="Title of the Proceedings", blank=True, null=True)
    conference_name = models.CharField(max_length=255, verbose_name="Name of the Conference", blank=True, null=True)
    national_international = models.CharField(
        max_length=50,
        choices=[('National', 'National'), ('International', 'International')],
        verbose_name="National / International"
    )
    publication_year = models.PositiveIntegerField(verbose_name="Year of Publication")
    isbn_issn = models.CharField(max_length=50, verbose_name="ISBN/ISSN", blank=True, null=True)
    affiliating_institute = models.CharField(max_length=255, verbose_name="Affiliating Institute", blank=True, null=True)
    publisher = models.CharField(max_length=255, verbose_name="Publisher")

    def __str__(self):
        return f"{self.book_title} by {self.teacher_name.user_profile.user.username} ({self.publication_year})"
    
class AdmittedStudent(models.Model):
    year = models.IntegerField()
    programme_name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="admitted_students")

    # Earmarked Seats
    sc_earmarked = models.IntegerField(default=0)
    st_earmarked = models.IntegerField(default=0)
    obc_earmarked = models.IntegerField(default=0)
    gen_earmarked = models.IntegerField(default=0)
    others_earmarked = models.IntegerField(default=0)

    # Admitted Students
    sc_admitted = models.IntegerField(default=0)
    st_admitted = models.IntegerField(default=0)
    obc_admitted = models.IntegerField(default=0)
    gen_admitted = models.IntegerField(default=0)
    others_admitted = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.programme_name} ({self.year}) - {self.department.name}"

class TeacherRecord(models.Model):
    """
    Model representing a Teacher's serving post details.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_records", verbose_name="Teacher Name")
    qualification_year = models.CharField(max_length=255, verbose_name="Qualification and Year of Obtaining")
    is_research_guide = models.BooleanField(default=False, verbose_name="Recognised as Research Guide")
    year_of_recognition = models.PositiveIntegerField(verbose_name="Year of Recognition as Research Guide", null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.name} - {self.qualification_year}"
    
class TeacherServingPost(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="serving_posts", verbose_name="Teacher")
    appointment_year = models.PositiveIntegerField(verbose_name="Appointment Year")
    nature_of_appointment = models.CharField(max_length=255, verbose_name="Nature of Appointment")
    experience_years = models.PositiveIntegerField(verbose_name="Years of Experience")
    is_serving = models.BooleanField(default=True, verbose_name="Is Still Serving?")
    last_year_service = models.PositiveIntegerField(null=True, blank=True, verbose_name="Last Year of Service")

    def __str__(self):
        return f"{self.teacher.user_profile.user.username} - {self.appointment_year}"
class FullTimeTeacher(models.Model):
    teacher_name = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE, 
        verbose_name="Name of Full-Time Teacher"
    )
    qualification_year = models.CharField(
        max_length=255, 
        verbose_name="Qualification (Ph.D./D.M/M.Ch./D.N.B Superspeciality/D.Sc./D’Lit.) and Year of Obtaining"
    )
    is_research_guide = models.BooleanField(
        default=False, 
        verbose_name="Whether Recognised as Research Guide"
    )
    year_of_recognition = models.PositiveIntegerField(
        null=True, blank=True, 
        verbose_name="Year of Recognition as Research Guide"
    )

    def __str__(self):
        return f"{self.teacher_name.name} ({self.qualification_year})"
    
class TeacherAgainstSanctionedPost(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name="Full-Time Teacher"
    )
    year_of_appointment = models.PositiveIntegerField(verbose_name="Year of Appointment")
    nature_of_appointment = models.CharField(
        max_length=255,
        choices=[
            ("Against Sanctioned Post", "Against Sanctioned Post"),
            ("Temporary", "Temporary"),
            ("Permanent", "Permanent"),
        ],
        verbose_name="Nature of Appointment"
    )
    years_of_experience = models.PositiveIntegerField(verbose_name="Total Years of Experience in the Same Institution")
    still_serving = models.CharField(
        max_length=255,
        verbose_name="Is the teacher still serving / Last year of service"
    )
    last_year_of_service = models.PositiveIntegerField(null=True, blank=True, verbose_name="Last Year of Service")  # Ensure the name matches
    def __str__(self):
        return f"{self.teacher.name} - {self.nature_of_appointment}"
class Programme(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programmes")
    programme_code = models.CharField(max_length=50, unique=True)
    programme_name = models.CharField(max_length=255)
    year_of_introduction = models.IntegerField()
    cbcs_status = models.CharField(max_length=15, choices=[('Yes', 'Yes'), ('No', 'No')])
    year_of_cbcs_implementation = models.IntegerField(null=True, blank=True)
    year_of_revision = models.IntegerField(null=True, blank=True)
    content_update_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Example: 50.00%
    document_link = models.URLField(null=True, blank=True)  # Link to related documentation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.programme_name} ({self.programme_code})"
    
class Course(models.Model):
    """
    Represents a course focusing on employability, entrepreneurship, or skill development.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
    name = models.CharField(max_length=100, verbose_name="Name of the Course")
    code = models.CharField(max_length=20, unique=True, verbose_name="Course Code")
    year_of_introduction = models.PositiveIntegerField(verbose_name="Year of Introduction")
    activities = models.TextField(verbose_name="Employability/Skill Development Activities")
    document = models.FileField(upload_to="course_documents/", null=True, blank=True, verbose_name="Relevant Document")

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class ValueAddedCourse(models.Model):
    """
    Model for Value-Added Courses.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses", verbose_name="Department")
    name = models.CharField(max_length=100, verbose_name="Course Name")
    code = models.CharField(max_length=20,verbose_name="Course Code")
    year_of_offering = models.PositiveIntegerField(verbose_name="Year of Offering")
    times_offered = models.PositiveIntegerField(default=1, verbose_name="Number of Times Offered")
    duration = models.CharField(max_length=50, verbose_name="Duration (e.g., 30 Hours)")
    students_enrolled = models.PositiveIntegerField(verbose_name="Students Enrolled")
    students_completed = models.PositiveIntegerField(verbose_name="Students Completed")
    document = models.FileField(upload_to="course_documents/", null=True, blank=True, verbose_name="Supporting Document")

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class StudentProject(models.Model):
    """
    Model representing a field project, research project, or internship.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="projects", verbose_name="Department")
    programme_name = models.CharField(max_length=100, verbose_name="Programme Name")
    programme_code = models.CharField(max_length=20, verbose_name="Programme Code")
    students = models.TextField(verbose_name="List of Students")
    document = models.FileField(upload_to="project_documents/", null=True, blank=True, verbose_name="Supporting Document")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.programme_name} ({self.programme_code})"