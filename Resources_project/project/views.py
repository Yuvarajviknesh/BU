from django.shortcuts import render, redirect,get_object_or_404,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
import os
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from .models import LibraryResource, UserProfile,Department,ICTFacility,EContentDevelopment,Teacher,Expenditure

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")  # Get the email from the form
        password = request.POST.get("password")  # Get the password from the form
        
        # Check if a user with the provided email exists
        try:
            user = User.objects.get(email=email)  # Fetch the user by email
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            # Authenticate using the username (which is required by authenticate)
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Login successful!")
                return redirect("home")  # Redirect to the home page after login
            else:
                messages.error(request, "Invalid password!")
        else:
            messages.error(request, "Invalid email address!")
    
    return render(request, "login.html")  # Render the login template

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")  # Redirect to login page after logout

@login_required  # Ensure that only authenticated users can access this view
def home_view(request):
    return render(request, "home.html")  # Home page template


def user_is_library_or_superuser(user):
    """Check if user is a superuser or belongs to the Library department."""
    if user.is_superuser:
        return True  # Admin can access everything
    try:
        return user.userprofile.is_library_user()
    except UserProfile.DoesNotExist:
        return False

@login_required
def library_resources(request):
    """Allow only Library Department users and superusers to view resources."""
    if request.user.is_superuser:
        resources = LibraryResource.objects.all()  # Admin sees everything
    elif user_is_library_or_superuser(request.user):
       resources = LibraryResource.objects.filter(department__department_name="Library") # Library users see only library data
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect("home")  # Redirect to home or another suitable page

    return render(request, 'Forms/library_resources.html', {'resources': resources})
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Must be before @login_required
@login_required
def update_library_resource(request, resource_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    resource = get_object_or_404(LibraryResource, id=resource_id)

    try:
        resource.academic_year = request.POST.get("academic_year", resource.academic_year)
        resource.resource_name = request.POST.get("resource_name", resource.resource_name)
        resource.expenditure_journals = float(request.POST.get("expenditure_journals", resource.expenditure_journals))
        resource.expenditure_other_resources = float(request.POST.get("expenditure_other_resources", resource.expenditure_other_resources))
        resource.total_expenditure = float(request.POST.get("total_expenditure", resource.total_expenditure))

        if "document" in request.FILES:
            resource.document = request.FILES["document"]

        resource.save()

        return JsonResponse({
            "success": True,
            "message": "Resource updated successfully",
            "updated_data": {
                "academic_year": resource.academic_year,
                "resource_name": resource.resource_name,
                "expenditure_journals": resource.expenditure_journals,
                "expenditure_other_resources": resource.expenditure_other_resources,
                "total_expenditure": resource.total_expenditure,
                "document_url": resource.document.url if resource.document else None
            }
        })

    except ValueError as e:
        return JsonResponse({"success": False, "error": f"Invalid data: {str(e)}"}, status=400)


def validate_pdf(file):
    """Checks if the uploaded file is a PDF and does not exceed 5MB."""
    if file:
        if not file.name.lower().endswith(".pdf"):
            return "Only PDF files are allowed."
        if file.size > 5 * 1024 * 1024:  # 5MB limit
            return "File size should not exceed 5MB."
    return None

@login_required
def add_library_resource(request):
    """Handles adding a new library resource to the database."""
    if request.method == "POST":
        academic_year = request.POST.get("academicYear")
        resource_name = request.POST.get("resourceName")
        expenditure_journals = request.POST.get("expenditureJournals")
        expenditure_other_resources = request.POST.get("expenditureOthers")
        total_expenditure = request.POST.get("totalExpenditure")
        document = request.FILES.get("document")

        # Validate PDF file
        error = validate_pdf(document)
        if error:
            messages.error(request, error)
            return redirect("add_library_resource")

        # Get the Library department instance
        try:
            library_department = Department.objects.get(department_name="Library")
        except Department.DoesNotExist:
            messages.error(request, "Library department not found.")
            return redirect("add_library_resource")

        # Convert expenditure values to float
        try:
            expenditure_journals = float(expenditure_journals)
            expenditure_other_resources = float(expenditure_other_resources)
            total_expenditure = float(total_expenditure)
        except ValueError:
            messages.error(request, "Invalid expenditure values entered.")
            return redirect("add_library_resource")

        # Save resource data in the database
        LibraryResource.objects.create(
            academic_year=academic_year,
            resource_name=resource_name,
            expenditure_journals=expenditure_journals,
            expenditure_other_resources=expenditure_other_resources,
            total_expenditure=total_expenditure,
            document=document,
            department=library_department
        )

        messages.success(request, "Library resource added successfully!")
        return redirect("library_resources")

    return render(request, "AddData/add_library_resource.html")

def delete_library_resource(request, id):
    resource = get_object_or_404(LibraryResource, id=id)
    resource.delete()
    return redirect('library_resources')  # Redirect to the main page after deletion

@login_required
def ict_facility_list(request):
    """ View all ICT facilities (admin sees all, department sees their own) """
    if request.user.is_staff:
        facilities = ICTFacility.objects.all()
    else:
        user_department = request.user.userprofile.department
        facilities = ICTFacility.objects.filter(department=user_department)

    return render(request, 'Forms/ict_facility_list.html', {'facilities': facilities})

@login_required
def add_ict_facility(request):
    """ Add a new ICT Facility """
    if request.method == "POST":
        department_code = request.POST.get("department", "").strip()
        room_type = request.POST.get("room_type", "").strip()
        room_no = request.POST.get("room_no", "").strip()
        ict_facility = request.POST.get("ict_facility", "").strip()
        geo_tagged_photo = request.FILES.get("geo_tagged_photo")  # Accepts file
        master_timetable = request.FILES.get("master_timetable")  # Accepts file

        if not (room_type and room_no and ict_facility and geo_tagged_photo and master_timetable):
            messages.error(request, "All fields are required!")
            return redirect("add_facility")

        department = get_object_or_404(Department, department_code=department_code)

        ICTFacility.objects.create(
            department=department,
            room_type=room_type,
            room_no=room_no,
            ict_facility=ict_facility,
            geo_tagged_photo=geo_tagged_photo,
            master_timetable=master_timetable,
        )

        messages.success(request, "New ICT Facility added successfully!")
        return redirect("ict_facility_list")

    departments = Department.objects.all()
    return render(request, "AddData/add_ict_facility.html", {"departments": departments})

@login_required
def update_facility(request, facility_id):
    """ Update ICT Facility using POST data """
    facility = get_object_or_404(ICTFacility, id=facility_id)

    if request.method == "POST":
        room_type = request.POST.get("room_type", "").strip()
        room_no = request.POST.get("room_no", "").strip()
        ict_facility = request.POST.get("ict_facility", "").strip()

        # Handling file uploads correctly
        geo_tagged_photo = request.FILES.get("geo_tagged_photo")
        master_timetable = request.FILES.get("master_timetable")

        # Validate required fields (excluding optional files)
        if not (room_type and room_no and ict_facility):
            messages.error(request, "Room Type, Room No, and ICT Facility are required!")
            return redirect("update_facility", facility_id=facility.id)

        # Update facility details
        facility.room_type = room_type
        facility.room_no = room_no
        facility.ict_facility = ict_facility

        # Only update file fields if a new file is uploaded
        if geo_tagged_photo:
            facility.geo_tagged_photo = geo_tagged_photo
        if master_timetable:
            facility.master_timetable = master_timetable

        facility.save()
        messages.success(request, "ICT Facility updated successfully!")
        return redirect("ict_facility_list")

    return render(request, "Forms/ict_facility_list.html", {"facility": facility})


@login_required
def delete_ict_facility(request, facility_id):
    facility = get_object_or_404(ICTFacility, id=facility_id)
    facility.delete()
    return redirect('ict_facility_list')

def add_econtent(request):
    if request.method == 'POST':
        name_teacher = request.POST.get('nameTeacher')  # Get Teacher ID or name
        module_name = request.POST.get('moduleName')
        platform = request.POST.get('platform')
        launch_date = request.POST.get('launchDate')
        document_link = request.FILES.get('docFile')
        facility_list = request.POST.get('facilityList')  # Comma-separated list
        video_link = request.POST.get('videoLink')

        # Convert facility list to JSON format
    
        # Retrieve the Teacher object
        teacher_obj = None
        if name_teacher.isdigit():  # If Teacher ID is selected from dropdown
            teacher_obj = Teacher.objects.get(id=int(name_teacher))
        else:  # If teacher's name is auto-filled
            teacher_obj = Teacher.objects.filter(user__username=name_teacher).first()

        # Check if teacher exists
        if not teacher_obj:
            messages.error(request, "Invalid teacher selection.")
            return redirect('add_econtent')

        # Save the new EContentDevelopment entry
        econtent = EContentDevelopment(
            teacher=teacher_obj,
            module_name=module_name,
            platform=platform,
            launch_date=launch_date,
            document_link=document_link,
            facility_available=facility_list,
            video_link=video_link
        )
        econtent.save()

        messages.success(request, "E-Content record added successfully.")
        return redirect('show_econtent')  # Redirect to list view

    # Fetch required data for rendering form
    teachers = Teacher.objects.all()
    user_role = request.user.groups.first().name if request.user.groups.exists() else "guest"
    
    logged_in_teacher = None
    if user_role == "teacher":
        try:
            logged_in_teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            messages.error(request, "You are not associated with a teacher record.")

    return render(request, 'AddData/add_econtent.html', {
        'teachers': teachers,
        'user_role': user_role,
        'logged_in_teacher': logged_in_teacher.user.username if logged_in_teacher else ""
    })



@login_required
def show_econtent(request):
    """Show records: Admins see all, teachers see only their own records."""
    if request.user.is_superuser:  
        records = EContentDevelopment.objects.all()
    else:
        # Fetch UserProfile first
        user_profile = get_object_or_404(UserProfile, user=request.user)
        
        # Fetch Teacher instance linked to the UserProfile
        teacher = get_object_or_404(Teacher, user_profile=user_profile)
        
        # Filter EContentDevelopment by the Teacher
        records = EContentDevelopment.objects.filter(teacher=teacher)

    return render(request, 'Forms/econtent_list.html', {'records': records})

@login_required
def edit_econtent(request, record_id):
    """Edit E-Content: Only the associated teacher or an admin can edit."""
    record = get_object_or_404(EContentDevelopment, id=record_id)

    if not request.user.is_superuser and request.user != record.teacher.user_profile.user:
        messages.error(request, "You are not authorized to edit this record.")
        return redirect('show_econtent')

    if request.method == "POST":
        record.module_name = request.POST.get("module_name")
        record.platform = request.POST.get("platform")

        launch_date_str = request.POST.get("launch_date")
        if launch_date_str:
            try:
                record.launch_date = datetime.strptime(launch_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('show_econtent')

        record.facility_available = request.POST.get("facility_available") 
        record.video_link = request.POST.get("video_link")

        # Handle file upload (retain existing file if no new file is uploaded)
        if 'document_link' in request.FILES:
            record.document_link = request.FILES['document_link']

        record.save()
        messages.success(request, "E-Content updated successfully!")
        return redirect('show_econtent')

    return redirect('show_econtent')

@login_required
def delete_econtent(request, record_id):
    """Delete E-Content: Only the associated teacher or an admin can delete."""
    record = get_object_or_404(EContentDevelopment, id=record_id)
    record.delete()
    messages.success(request,"E-Content deleted successfully! ")
    return redirect('show_econtent')

@login_required
def expenditure_list(request):
    if request.user.is_superuser:
        records = Expenditure.objects.all()
    else:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        records = Expenditure.objects.filter(department=user_profile.department)

    return render(request, 'Forms/expenditure_list.html', {'expenditures': records})

@login_required
def edit_expenditure(request, record_id):
    """Edit Expenditure: Only the associated department user or an admin can edit."""
    expenditure = get_object_or_404(Expenditure, id=record_id)

    # Restrict normal users from editing other departments' expenditures
    if not request.user.is_superuser and expenditure.department != request.user.userprofile.department:
        messages.error(request, "You are not authorized to edit this record.")
        return redirect("expenditure_list")

    if request.method == "POST":
        try:
            expenditure.year = request.POST.get("year")
            expenditure.budget_allocated = request.POST.get("budget_allocated")
            expenditure.expenditure_infra = request.POST.get("expenditure_infra")
            expenditure.academic_facilities = request.POST.get("academic_facilities")
            expenditure.physical_facilities = request.POST.get("physical_facilities")
            expenditure.total_expenditure = request.POST.get("total_expenditure_excluding_salary")

            # Convert values to float for validation
            budget_allocated = float(expenditure.budget_allocated) if expenditure.budget_allocated else 0
            expenditure_infra = float(expenditure.expenditure_infra) if expenditure.expenditure_infra else 0
            academic_facilities = float(expenditure.academic_facilities) if expenditure.academic_facilities else 0
            physical_facilities = float(expenditure.physical_facilities) if expenditure.physical_facilities else 0
            total_expenditure = float(expenditure.total_expenditure) if expenditure.total_expenditure_excluding_salary else 0

            # Ensure values are non-negative
            if any(value < 0 for value in [budget_allocated, expenditure_infra, academic_facilities, physical_facilities, total_expenditure]):
                messages.error(request, "Values cannot be negative.")
                return redirect("expenditure_list")

            # Save updated data
            expenditure.save()

            messages.success(request, "Expenditure record updated successfully.")
            return redirect("expenditure_list")

        except ValueError:
            messages.error(request, "Invalid input. Please enter valid numeric values.")
            return redirect("expenditure_list")

    return redirect("expenditure_list")

@login_required
def delete_expenditure(request, record_id):
    expenditure = get_object_or_404(Expenditure, id=record_id)

    # Restrict normal users from deleting other departments' expenditures
    if not request.user.is_superuser and expenditure.department != request.user.userprofile.department:
        messages.error(request, "Unauthorized access: You cannot delete this record.")
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    try:
        expenditure.delete()
        messages.success(request, "Expenditure record deleted successfully.")
        return redirect('expenditure_list')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('expenditure_list')

def add_expenditure(request):
    if request.method == "POST":
        user_profile = UserProfile.objects.get(user=request.user)  # Get logged-in user's profile
        department = user_profile.department  # Fetch department from the profile

        if not department:
            messages.error(request, "You do not have a department assigned.")
            return redirect("add_expenditure")

        try:
            year = int(request.POST.get("year", 0))
            budget = float(request.POST.get("budget", 0))
            expenditure = float(request.POST.get("expenditure", 0))
            total_expenditure = float(request.POST.get("total_expenditure", 0))
            academic_expenditure = float(request.POST.get("academic_expenditure", 0))
            physical_expenditure = float(request.POST.get("physical_expenditure", 0))

            # ✅ Define the max limit based on DecimalField(max_digits=12, decimal_places=2)
            MAX_VALUE = 9999999999.99  

            # ✅ Check if any value exceeds the allowed limit
            if budget > MAX_VALUE:
                messages.error(request, "Budget allocated exceeds the maximum allowed limit.")
            if expenditure > MAX_VALUE:
                messages.error(request, "Infrastructure expenditure exceeds the maximum allowed limit.")
            if total_expenditure > MAX_VALUE:
                messages.error(request, "Total expenditure exceeds the maximum allowed limit.")
            if academic_expenditure > MAX_VALUE:
                messages.error(request, "Academic facilities expenditure exceeds the maximum allowed limit.")
            if physical_expenditure > MAX_VALUE:
                messages.error(request, "Physical facilities expenditure exceeds the maximum allowed limit.")

            # ✅ If any error messages exist, return to the form without saving
            if messages.get_messages(request):
                return redirect("add_expenditure")

            # ✅ Save data if all values are within the limit
            Expenditure.objects.create(
                department=department,
                year=year,
                budget_allocated=budget,
                expenditure_infra=expenditure,
                total_expenditure=total_expenditure,
                academic_facilities=academic_expenditure,
                physical_facilities=physical_expenditure
            )

            messages.success(request, "Expenditure added successfully!")
            return redirect("expenditure_list")  # Redirect to the expenditure list page

        except ValueError:
            messages.error(request, "Invalid input! Please enter valid numbers.")
            return redirect("add_expenditure")

    return render(request, "AddData/add_expenditure.html")
