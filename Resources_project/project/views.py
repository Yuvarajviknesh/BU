from django.shortcuts import render, redirect,get_object_or_404,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
import os
import pandas as pd
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from .models import LibraryResource, UserProfile,Department,ICTFacility,EContentDevelopment,Teacher,Expenditure,TeacherAward,ResearchGrant,Investigator,AwardRecognition,Patent,PhDAward,DemandRatio
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email address!")
            return redirect("user_login")

        # Authenticate user
        auth_user = authenticate(request, username=user.username, password=password)

        if auth_user is not None and auth_user.is_active:
            login(request, auth_user)
            messages.success(request, "Login successful!")

            # Check if UserProfile exists
            user_profile = UserProfile.objects.filter(user=user).first()
            if not user_profile:
                messages.error(request, "User profile not found. Contact Admin.")
                logout(request)
                return redirect("user_login")

            # Redirect based on role
            if user_profile.is_department_staff:
                return redirect("department_dashboard")
            elif user_profile.is_scholar:
                return redirect("scholar_dashboard")
            elif user_profile.is_teacher:
                return redirect("staff_dashboard")  # Teachers -> Staff Dashboard

            # If no role is assigned, logout user
            messages.error(request, "You are not authorized to access this system.")
            logout(request)
            return redirect("user_login")

        else:
            messages.error(request, "Invalid credentials!")
            return redirect("user_login")

    return render(request, "login.html")


@login_required
def department_dashboard(request):
    try:
        profile = request.user.userprofile
        if not profile.is_department_staff:
            messages.error(request, "You are not authorized to access this page.")
            return redirect("login")
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("login")

    return render(request, "department_dashboard.html")

@login_required
def staff_dashboard(request):
    try:
        profile = request.user.userprofile
        if not profile.is_teacher:
            messages.error(request, "You are not authorized to access this page.")
            return redirect("login")
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("login")

    return render(request, "staff_dashboard.html")

@login_required
def scholar_dashboard(request):
    try:
        profile = request.user.userprofile
        if not profile.is_scholar:
            messages.error(request, "You are not authorized to access this page.")
            return redirect("login")
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("login")

    return render(request, "scholar_dashboard.html")



@login_required
def department_dashboard(request):
    # Ensure UserProfile exists and check `is_department_staff`
    if not hasattr(request.user, "userprofile") or not request.user.userprofile.is_department_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("home")
    
    return render(request, "department_dashboard.html")


@login_required
def scholar_dashboard(request):
    # Ensure UserProfile exists and check `is_scholar`
    if not hasattr(request.user, "userprofile") or not request.user.userprofile.is_scholar:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("home")
    
    return render(request, "scholar_dashboard.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")  # Redirect to login page after logout

@login_required
def home_view(request):
    return render(request, "home.html",  {'disable_filter': True})

def criterion_page(request, criterion_number):
    request.session['criterion_id'] = criterion_number
    return render(request, 'criterion.html', {'criterion_id': criterion_number})

def user_is_library_or_superuser(user):
    """Check if user is a superuser or belongs to the Library department."""
    if user.is_superuser:
        return True  # Admin can access everything
    try:
        return user.userprofile.is_library_user()
    except UserProfile.DoesNotExist:
        return False

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
import openpyxl
from .models import LibraryResource, Department

@login_required
def library_resources(request):
    """
    List, filter, and export Library Resources:
    - Superusers see all resources.
    - Library department staff see only their department’s resources.
    - Teachers and unauthorized users are restricted.
    """
    current_year = datetime.now().year
    years = list(range(2000, current_year + 1))
    # Fetch the user and their profile
    user = request.user
    user_profile = getattr(user, 'userprofile', None)

    # Access Control
    if user.is_superuser:
        # Superusers see all data
        resources = LibraryResource.objects.all()
        departments = Department.objects.all()
    elif user_profile and user_profile.department and user_profile.department.department_name == "Library":
        # Library staff see their department's resources
        resources = LibraryResource.objects.filter(department=user_profile.department)
        departments = Department.objects.filter(department_code=user_profile.department.department_code)
    else:
        # Unauthorized users are redirected
        messages.error(request, "You are not authorized to view this page.")
        return redirect("home")

    # Apply Filters
    selected_department = request.GET.get('department')
    year_from = request.GET.get('year_from')
    year_to = request.GET.get('year_to')
    resource_name = request.GET.get('resource_name')

    if selected_department:
        resources = resources.filter(department__id=selected_department)
    if year_from and year_to:
        resources = resources.filter(academic_year__range=(year_from, year_to))
    elif year_from:
        resources = resources.filter(academic_year__gte=year_from)
    elif year_to:
        resources = resources.filter(academic_year__lte=year_to)
    if resource_name:
        resources = resources.filter(resource_name=resource_name)

    # Export to Excel
    if 'export_excel' in request.GET:
        # Create an Excel workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Library Resources"

        # Add headers
        sheet.append(['Academic Year', 'Resource Name', 'Expenditure on e-Journals/Books',
                      'Expenditure on Other e-Resources', 'Total Expenditure', 'Department'])

        # Add data rows
        for resource in resources:
            sheet.append([
                resource.academic_year,
                resource.resource_name,
                resource.expenditure_journals,
                resource.expenditure_other_resources,
                resource.total_expenditure,
                resource.department.department_name,
            ])

        # Return response as an Excel file
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=LibraryResources.xlsx'
        workbook.save(response)
        return response

    # Pagination
    paginator = Paginator(resources, 10)  # Show 10 resources per page
    page_number = request.GET.get('page')
    resources = paginator.get_page(page_number)

    # Context for rendering
    context = {
        "resources": resources,
        "departments": departments,
        "selected_department": selected_department,
        "year_from": year_from,
        "year_to": year_to,
        "resource_name": resource_name,
        "years": years,
    }

    return render(request, 'Forms/library_resources.html', context)

@login_required
def download_library_resources_excel(request):
    """Export Library Resources data to an Excel file with authorization checks."""

    user = request.user

    # **Check if user has a UserProfile**
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponse("Unauthorized: No user profile found", status=403)

    # **Authorization Logic**
    if user.is_superuser:
        resources = LibraryResource.objects.all()
    elif user_profile.is_department_staff:
        if user_profile.department:
            resources = LibraryResource.objects.filter(department=user_profile.department)
        else:
            return HttpResponse("Unauthorized: No department assigned", status=403)
    else:
        return HttpResponse("Unauthorized: Insufficient permissions", status=403)

    # **Filtering Logic**
    year_from = request.GET.get("year_from")
    year_to = request.GET.get("year_to")
    resource_name = request.GET.get("resource_name")

    if year_from and year_to:
        resources = resources.filter(academic_year__range=(year_from, year_to))
    elif year_from:
        resources = resources.filter(academic_year__gte=year_from)
    elif year_to:
        resources = resources.filter(academic_year__lte=year_to)
    if resource_name:
        resources = resources.filter(resource_name=resource_name)

    # **Create an Excel Workbook**
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Library Resources"

    # **Header Row**
    headers = ["Academic Year", "Resource Name", "Expenditure on e-Journals/Books",
               "Expenditure on Other e-Resources", "Total Expenditure", "Department", "Downloaded By"]
    sheet.append(headers)

    # **Add Data Rows**
    for resource in resources:
        sheet.append([
            resource.academic_year,
            resource.resource_name,
            resource.expenditure_journals,
            resource.expenditure_other_resources,
            resource.total_expenditure,
            resource.department.department_name if resource.department else "N/A",
            f"{user.username} ({getattr(user_profile, 'position', 'N/A')})",  # Capture username & position
        ])

    # **Prepare HTTP Response**
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="LibraryResources.xlsx"'
    workbook.save(response)
    
    return response


@login_required
def download_library_resource_pdf(request, resource_id):
    """
    Generate and download a PDF for Library Resource details.
    """
    resource = get_object_or_404(LibraryResource, id=resource_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="library_resource_{resource.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Background Color
    pdf.setFillColorRGB(0.95, 0.95, 0.95)  # Light Gray
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    # Logo
    logo_path = finders.find("images/logo2.png")  # Replace with your logo path
    if not logo_path:
        raise OSError("Logo file not found in static directory!")
    logo = ImageReader(logo_path)

    # Header with Blue Background
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, height - 100, width - 40, 80, 10, fill=True, stroke=False)

    # Header Text
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 60, "Library Resource Details")
    pdf.drawImage(logo, 50, height - 85, width=140, height=50, mask="auto")

    # Table Data
    data = [
        ["Academic Year", resource.academic_year],
        ["Resource Name", resource.resource_name],
        ["Expenditure on e-Journals/Books", f"₹{resource.expenditure_journals}"],
        ["Expenditure on Other e-Resources", f"₹{resource.expenditure_other_resources}"],
        ["Total Library Expenditure", f"₹{resource.total_expenditure}"],
        ["Department", resource.department.department_name],
    ]

    table = Table(data, colWidths=[200, 280])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.blue),
        ("BOX", (0, 0), (-1, -1), 2, colors.blue),
    ]))

    # Draw Table in Center
    table_x = (width - 480) / 2
    table_y = height - 280
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, table_x, table_y)

    # Footer with Blue Background
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, 20, width - 40, 50, 10, fill=True, stroke=False)

    # Footer Text
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, 45, "© 2025 Bharathiar University. All Rights Reserved.")

    # Curved Double Line Border
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.roundRect(10, 10, width - 20, height - 20, 15, stroke=True, fill=False)
    pdf.roundRect(15, 15, width - 30, height - 30, 12, stroke=True, fill=False)

    pdf.showPage()
    pdf.save()

    return response

@login_required
def library_resource_detail(request, resource_id):
    """
    Show details for a specific Library Resource.
    """
    resource = get_object_or_404(LibraryResource, id=resource_id)
    return render(request, 'viewData/library_resource_detail.html', {'resource': resource})

@login_required
def update_library_resource(request, resource_id):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("library_resources")  # Redirect to your library resources page

    resource = get_object_or_404(LibraryResource, id=resource_id)

    try:
        # Update fields with form data
        resource.academic_year = request.POST.get("academic_year", resource.academic_year)
        resource.resource_name = request.POST.get("resource_name", resource.resource_name)
        resource.expenditure_journals = float(request.POST.get("expenditure_journals", resource.expenditure_journals))
        resource.expenditure_other_resources = float(request.POST.get("expenditure_other_resources", resource.expenditure_other_resources))
        resource.total_expenditure = float(request.POST.get("total_expenditure", resource.total_expenditure))

        # Handle document upload if provided
        if "document" in request.FILES:
            resource.document = request.FILES["document"]

        resource.save()
        messages.success(request, "Library resource updated successfully.")
        return redirect("library_resources") 

    except ValueError as e:
        messages.error(request, f"Invalid data provided: {str(e)}")
        return redirect("library_resources")

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("library_resources")


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
        criterion_id = request.session.get('criterion_id')
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

    return render(request, "AddData/add_library_resource.html", {'disable_filter': True})

def delete_library_resource(request, resource_id):
    resource = get_object_or_404(LibraryResource, id=resource_id)
    resource.delete()
    return redirect('library_resources')  # Redirect to the main page after deletion
@login_required
def ict_facility_list(request):
    """
    List and filter ICT Facilities:
    - Superusers see all data.
    - Department staff see data related to their department.
    - Teachers see only their related department data.
    """

    # Fetch the user and their profile
    user = request.user
    user_profile = getattr(user, 'userprofile', None)

    # Fetch filter values from GET request
    department_id = request.GET.get('department', '')
    room_type = request.GET.get('room_type', '')
    ict_facility = request.GET.get('ict_facility', '')

    # Initialize the facilities queryset and restrict access based on roles
    if user.is_superuser:
        # Superusers see all facilities
        facilities = ICTFacility.objects.all()
        departments = Department.objects.all()
    elif user_profile and user_profile.is_department_staff:
        # Department staff see only their department's facilities
        facilities = ICTFacility.objects.filter(department=user_profile.department)
        departments = Department.objects.filter(department_code=user_profile.department.department_code)
    elif user_profile and user_profile.is_teacher:
        # Teachers see only their department's facilities
        if user_profile.department:
            facilities = ICTFacility.objects.filter(department=user_profile.department)
            departments = Department.objects.filter(department_code=user_profile.department.department_code)
        else:
            facilities = ICTFacility.objects.none()
            departments = Department.objects.none()
    else:
        # For users without a proper profile, return no data
        facilities = ICTFacility.objects.none()
        departments = Department.objects.none()

    # Apply additional filters if provided in the GET request
    if department_id:
        facilities = facilities.filter(department_id=department_id)
    if room_type:
        facilities = facilities.filter(room_type__icontains=room_type)  # Case-insensitive matching
    if ict_facility:
        facilities = facilities.filter(ict_facility__icontains=ict_facility)

    # Add pagination for scalability
    from django.core.paginator import Paginator
    paginator = Paginator(facilities, 10)  # Show 10 facilities per page
    page_number = request.GET.get('page')
    facilities = paginator.get_page(page_number)

    # Context for rendering the template
    context = {
        'facilities': facilities,
        'departments': departments,
        'selected_department': department_id,
        'selected_room_type': room_type,
        'selected_ict_facility': ict_facility,
    }

    return render(request, 'Forms/ict_facility_list.html', context)

@login_required
def download_ict_facilities(request):
    """Generate and download an Excel file containing ICT facilities details based on user role."""

    user = request.user

    # **Check if user has a UserProfile**
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponse("Unauthorized: No user profile found", status=403)

    # **Authorization Logic**
    if user.is_superuser:
        facilities = ICTFacility.objects.all()
    elif user_profile.is_department_staff:
        if user_profile.department:
            facilities = ICTFacility.objects.filter(department=user_profile.department)
        else:
            return HttpResponse("Unauthorized: No department assigned", status=403)
    else:
        return HttpResponse("Unauthorized: Insufficient permissions", status=403)

    # **Prepare Data**
    data = []
    for facility in facilities:
        data.append({
            "Department Code": facility.department.department_code,
            "Department Name": facility.department.department_name,
            "Room Type": facility.room_type,
            "Room No": facility.room_no,
            "Type of ICT Facility": facility.ict_facility,
            "Geo-Tagged Photo": facility.geo_tagged_photo.url if facility.geo_tagged_photo else "No Image",
            "Master Time Table": facility.master_timetable.url if facility.master_timetable else "No Timetable",
            "Downloaded By": f"{user.username} ({getattr(user_profile, 'position', 'N/A')})",  # Capture username & position
        })

    # **Convert to DataFrame**
    df = pd.DataFrame(data)

    # **Create HTTP response with Excel file**
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ICT_Facilities.xlsx"'

    # **Write to Excel file**
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ICT Facilities')

    return response

from reportlab.pdfgen import canvas

def facility_detail(request, facility_id):
    facility = get_object_or_404(ICTFacility, id=facility_id)
    return render(request, "viewData/facility_detail.html", {"facility": facility})

def download_facility_pdf(request, facility_id):
    facility = get_object_or_404(ICTFacility, id=facility_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facility_{facility.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4  

    # **Background Color for Entire Page**
    pdf.setFillColorRGB(0.95, 0.95, 0.95)  # Light Gray Background
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    # ✅ Find Logo File
    logo_path = finders.find("images/logo2.png")
    if not logo_path:
        raise OSError("Logo file not found in static directory!")

    logo = ImageReader(logo_path)

    # **Header Section with Blue Background**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, height - 100, width - 40, 80, 10, fill=True, stroke=False)  # ✅ Rounded Header

    # **Header Text**
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 60, "ICT Facility Details")

    pdf.drawImage(logo, 50, height - 85, width=140, height=50, mask="auto")

    # **Table Data**
    data = [
        ["Department Code", facility.department.department_code],
        ["Department Name", facility.department.department_name],
        ["Room Type", facility.room_type],
        ["Room No", facility.room_no],
        ["Type of ICT Facility", facility.ict_facility]
    ]

    table = Table(data, colWidths=[200, 280])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.blue),  # ✅ Blue Borders
        ("BOX", (0, 0), (-1, -1), 2, colors.blue),   # ✅ Outer Blue Border
    ]))

    # **Draw Table in Center**
    table_x = (width - 480) / 2  
    table_y = height - 280  
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, table_x, table_y)

    # **Footer Section with Blue Background**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, 20, width - 40, 50, 10, fill=True, stroke=False)  # ✅ Rounded Footer

    # **Footer Text Without Logo**
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, 45, "© 2025 Bharathiar University. All Rights Reserved.")

    # **Curved Double Line Border for A4 Page**
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.roundRect(10, 10, width - 20, height - 20, 15, stroke=True, fill=False)  # ✅ Outer Border
    pdf.roundRect(15, 15, width - 30, height - 30, 12, stroke=True, fill=False)  # ✅ Inner Border

    pdf.showPage()
    pdf.save()
    
    return response

@login_required
def add_ict_facility(request):
    """ Add a new ICT Facility """
    criterion_id = request.session.get('criterion_id')
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
    return render(request, "AddData/add_ict_facility.html", {"departments": departments,'criterion_id':criterion_id, 'disable_filter': True})

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
def view_econtent_detail(request, record_id):
    econtent = get_object_or_404(EContentDevelopment, id=record_id)
    return render(request, "viewData/econtent_detail.html", {"econtent": econtent})
@login_required
def download_econtent_excel(request):
    """Generate and download an Excel file for the logged-in user's E-Content records."""

    user = request.user

    # **Check if the user has a UserProfile**
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponse("Unauthorized: No user profile found", status=403)

    # **Determine access level**
    if user.is_superuser:
        records = EContentDevelopment.objects.all()
    elif user_profile.is_teacher:
        records = EContentDevelopment.objects.filter(teacher__user_profile=user_profile)
    elif user_profile.is_department_staff:
        if user_profile.department:
            records = EContentDevelopment.objects.filter(teacher__user_profile__department=user_profile.department)
        else:
            return HttpResponse("Unauthorized: No department assigned", status=403)
    else:
        return HttpResponse("Unauthorized: Insufficient permissions", status=403)

    # **Create Excel file**
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "E-Content Records"

    # **Headers**
    headers = ["Module Name", "Platform", "Launch Date", "Teacher (Position)", "Department", "Facilities", "Document Available", "Video Link"]
    ws.append(headers)

    # **Populate rows**
    for record in records:
        teacher = record.teacher
        teacher_name = teacher.user_profile.user.username if teacher else "N/A"
        teacher_position = f" ({teacher.position})" if teacher and teacher.position else ""
        teacher_full_name = f"{teacher_name}{teacher_position}"

        ws.append([
            record.module_name,
            record.platform,
            record.launch_date.strftime("%Y-%m-%d") if record.launch_date else "N/A",
            teacher_full_name,
            teacher.user_profile.department.department_name if teacher and teacher.user_profile.department else "N/A",
            record.facility_available,
            "Yes" if record.document_link else "No",
            record.video_link if record.video_link else "N/A",
        ])

    # **Prepare HTTP response**
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="E_Content_Records.xlsx"'

    wb.save(response)
    return response

@login_required
def delete_ict_facility(request, facility_id):
    facility = get_object_or_404(ICTFacility, id=facility_id)
    facility.delete()
    return redirect('ict_facility_list')

def add_econtent(request):
    criterion_id = request.session.get('criterion_id')
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
        'criterion_id':criterion_id,
        'logged_in_teacher': logged_in_teacher.user.username if logged_in_teacher else "",
        'disable_filter': True
    })

@login_required
def show_econtent(request):
    """Display E-Content records based on user roles with filters."""
    
    user = request.user
    current_year = datetime.now().year
    year_range = range(2000, current_year + 1)  # Generate years from 2000 to current year
    is_superuser = user.is_superuser
    user_profile = get_object_or_404(UserProfile, user=user) if not is_superuser else None

    # Initialize filters
    selected_teacher = request.GET.get('teacher')
    selected_department = request.GET.get('department')
    from_year = request.GET.get('from_year')
    to_year = request.GET.get('to_year')

    # Superuser: See all records, departments, and teachers
    if is_superuser:
        records = EContentDevelopment.objects.all()
        departments = Department.objects.all()
        teachers = Teacher.objects.all()

    # Department Staff: View all teachers in their department
    elif user_profile.is_department_staff and user_profile.department:
        department = user_profile.department
        records = EContentDevelopment.objects.filter(teacher__user_profile__department=department)
        departments = Department.objects.filter(department_code=department.department_code)
        teachers = Teacher.objects.filter(user_profile__department=department)

    # Teachers: See only their own records
    elif user_profile.is_teacher:
        teacher = get_object_or_404(Teacher, user_profile=user_profile)
        records = EContentDevelopment.objects.filter(teacher=teacher)
        departments = Department.objects.filter(department_code=user_profile.department.department_code)
        teachers = None  # No teacher dropdown needed

    # Unauthorized users: No access
    else:
        records = EContentDevelopment.objects.none()
        departments = Department.objects.none()
        teachers = None

    # Apply Filters
    if from_year:
        records = records.filter(launch_date__year__gte=from_year)
    if to_year:
        records = records.filter(launch_date__year__lte=to_year)
    if selected_teacher and teachers:
        records = records.filter(teacher_id=selected_teacher)
    if selected_department and departments:
        records = records.filter(teacher__user_profile__department__department_code=selected_department)

    context = {
        "records": records,  
        "departments": departments,  
        "teachers": teachers,  
        "year_range": year_range,
        "selected_teacher": selected_teacher,
        "selected_department": selected_department,
        "from_year": from_year,
        "to_year": to_year,
        "is_superuser": is_superuser,
        "is_department_staff": getattr(user_profile, 'is_department_staff', False),
    }

    return render(request, 'Forms/econtent_list.html', context)
def download_econtent_pdf(request, econtent_id):
    """Generate and download a PDF for a single viewed E-Content Development record."""
    
    econtent = get_object_or_404(EContentDevelopment, id=econtent_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="econtent_{econtent.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4  

    # **Background Color**
    pdf.setFillColorRGB(0.95, 0.95, 0.95)
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    # **Find Logo File**
    try:
        logo_path = finders.find("images/logo2.png")
        if logo_path:
            logo = ImageReader(logo_path)
            pdf.drawImage(logo, 50, height - 85, width=140, height=50, mask="auto")
    except Exception as e:
        print(f"Error loading logo: {e}")

    # **Header Section**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, height - 100, width - 40, 80, 10, fill=True, stroke=False)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 60, "E-Content Development Details")

    # **Retrieve Safe Data**
    teacher_name = econtent.teacher.user_profile.user.username  if econtent.teacher else "N/A"
    position= econtent.teacher.position if econtent.teacher else "N/A"
    department_name = econtent.teacher.user_profile.department.department_name if econtent.teacher and econtent.teacher.user_profile.department else "N/A"
    document_status = "Available" if econtent.document_link else "Not Available"
    video_status = econtent.video_link if econtent.video_link else "N/A"

    # **Table Data**
    data = [
        ["Module Name", econtent.module_name],
        ["Platform", econtent.platform],
        ["Launch Date", econtent.launch_date.strftime("%d-%m-%Y") if econtent.launch_date else "N/A"],
        ["Teacher", teacher_name + " (" + position + ")"],
        ["Department", department_name],
        ["Facilities", econtent.facility_available],
        ["Document", document_status],
        ["Video Link", video_status]
    ]

    table = Table(data, colWidths=[200, 280])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.blue),
        ("BOX", (0, 0), (-1, -1), 2, colors.blue),
    ]))

    table_x = (width - 480) / 2  
    table_y = height - 280  
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, table_x, table_y)

    # **Footer Section**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, 20, width - 40, 50, 10, fill=True, stroke=False)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, 45, "© 2025 Bharathiar University. All Rights Reserved.")

    # **Curved Double Line Border**
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.roundRect(10, 10, width - 20, height - 20, 15, stroke=True, fill=False)
    pdf.roundRect(15, 15, width - 30, height - 30, 12, stroke=True, fill=False)

    pdf.showPage()
    pdf.save()
    
    return response



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
    """Show Expenditure records with filters based on user roles (Admins see all, department users see their own)."""

    # ✅ Get filter parameters from the request
    selected_department = request.GET.get('department', None)  # For department filtering
    year_from = request.GET.get('year_from', None)  # Year From Filter
    year_to = request.GET.get('year_to', None)      # Year To Filter

    # Determine the records based on the user's role
    if request.user.is_superuser:
        # Superuser can access all expenditure records
        records = Expenditure.objects.all()

        # Apply department filter if provided
        if selected_department:
            records = records.filter(department__department_code=selected_department)
    else:
        # Non-superuser (department users) can only access their department's data
        user_profile = get_object_or_404(UserProfile, user=request.user)
        if user_profile.department:
            records = Expenditure.objects.filter(department=user_profile.department)
        else:
            # No department assigned, no access to expenditure data
            records = Expenditure.objects.none()

    # Apply year filters (if provided)
    if year_from and year_to:
        records = records.filter(year__gte=year_from, year__lte=year_to)
    elif year_from:
        records = records.filter(year__gte=year_from)
    elif year_to:
        records = records.filter(year__lte=year_to)

    # Fetch departments for filtering dropdown
    if request.user.is_superuser:
        # Superuser sees all departments
        departments = Department.objects.all()
    else:
        # Department users see their own department only
        departments = Department.objects.filter(department_code=user_profile.department.department_code)

    # ✅ Context for the template
    context = {
        "departments": departments,
        "selected_department": selected_department,
        "year_from": year_from,
        "year_to": year_to,
        "expenditures": records,  # Pass the filtered expenditure records
    }

    return render(request, 'Forms/expenditure_list.html', context)
@login_required
def download_expenditure_excel(request):
    """Export expenditure data to an Excel file."""
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Expenditures"

    # Add headers
    headers = [
        "Year", "Department", "Budget Allocated",
        "Expenditure on Infrastructure", "Expenditure on Maintenance of Academic Facilities",
        "Expenditure on Maintenance of Physical Facilities", "Total Expenditure Excluding Salary"
    ]
    sheet.append(headers)

    # Add data rows
    expenditures = Expenditure.objects.all()
    for expenditure in expenditures:
        sheet.append([
            expenditure.year,
            expenditure.department.department_name,
            expenditure.budget_allocated,
            expenditure.expenditure_infra,
            expenditure.academic_facilities,
            expenditure.physical_facilities,
            expenditure.total_expenditure
        ])

    # Set up the response for downloading
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Expenditures.xlsx"'
    workbook.save(response)

    return response

@login_required
def view_expenditure_detail(request, expenditure_id):
    """
    Display the details of a specific expenditure record.
    """
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)  # Get the record or return 404
    context = {'expenditure': expenditure }
    return render(request, 'viewData/expenditure_detail.html', context)
@login_required
def download_expenditure_pdf(request, expenditure_id):
    """
    Generate and download a PDF for a specific Expenditure record.
    """
    # Get the expenditure record
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)

    # Set up the HTTP response for a PDF file
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="expenditure_{expenditure.year}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # **Background Color**
    pdf.setFillColorRGB(0.95, 0.95, 0.95)
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    # **Add Logo**
    try:
        logo_path = finders.find("images/logo2.png")  # Ensure the path is correct in static files
        if logo_path:
            logo = ImageReader(logo_path)
            pdf.drawImage(logo, 50, height - 85, 140, 50, mask="auto")
        else:
            print("Logo file not found.")
    except Exception as e:
        print(f"Error loading logo: {e}")

    # **Header Section**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, height - 100, width - 40, 80, 10, fill=True, stroke=False)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 60, "Expenditure Details")

    # **Table Data**
    department_name = expenditure.department.department_name if expenditure.department else "N/A"
    data = [
        ["Year", expenditure.year],
        ["Department", department_name],
        ["Budget Allocated", f"₹ {expenditure.budget_allocated:,}"],
        ["Expenditure on Infrastructure", f"₹ {expenditure.expenditure_infra:,}"],
        ["Expenditure on Academic Facilities", f"₹ {expenditure.academic_facilities:,}"],
        ["Expenditure on Physical Facilities", f"₹ {expenditure.physical_facilities:,}"],
        ["Total Expenditure Excluding Salary", f"₹ {expenditure.total_expenditure:,}"],
    ]

    # **Style Table**
    table = Table(data, colWidths=[250, 250])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.blue),
        ("BOX", (0, 0), (-1, -1), 2, colors.blue),
    ]))

    # **Draw Table**
    table_x = (width - 500) / 2
    table_y = height - 300
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, table_x, table_y)

    # **Footer Section**
    pdf.setFillColor(colors.blue)
    pdf.roundRect(20, 20, width - 40, 50, 10, fill=True, stroke=False)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, 45, f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    pdf.drawCentredString(width / 2, 30, "© 2025 Bharathiar University. All Rights Reserved.")

    # **Curved Double Line Border**
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.roundRect(10, 10, width - 20, height - 20, 15, stroke=True, fill=False)
    pdf.roundRect(15, 15, width - 30, height - 30, 12, stroke=True, fill=False)

    pdf.showPage()
    pdf.save()

    return response
 
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
            # Fetch values safely and convert them to proper data types
            expenditure.year = int(request.POST.get("year", expenditure.year))
            expenditure.budget_allocated = float(request.POST.get("budget_allocated", 0))
            expenditure.expenditure_infra = float(request.POST.get("expenditure_infra", 0))
            expenditure.academic_facilities = float(request.POST.get("academic_facilities", 0))
            expenditure.physical_facilities = float(request.POST.get("physical_facilities", 0))
            expenditure.total_expenditure = float(request.POST.get("total_expenditure_excluding_salary", 0))

            # Ensure values are non-negative
            if any(value < 0 for value in [
                expenditure.budget_allocated,
                expenditure.expenditure_infra,
                expenditure.academic_facilities,
                expenditure.physical_facilities,
                expenditure.total_expenditure
            ]):
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
    criterion_id = request.session.get('criterion_id')
    if request.method == "POST":
        #  Allow admins to proceed without a UserProfile
        if request.user.is_superuser:
            department = None  # Admins may not have a department
        else:
            try:
                user_profile = UserProfile.objects.get(user=request.user)  # Get logged-in user's profile
                department = user_profile.department
            except UserProfile.DoesNotExist:
                messages.error(request, "Your profile does not exist. Please contact the admin.")
                return redirect("add_expenditure")

        # Ensure a department is assigned (except for admins)
        if not department and not request.user.is_superuser:
            messages.error(request, "You do not have a department assigned.")
            return redirect("add_expenditure")

        try:
            year = int(request.POST.get("year", 0))
            budget = float(request.POST.get("budget", 0))
            expenditure = float(request.POST.get("expenditure", 0))
            total_expenditure = float(request.POST.get("total_expenditure", 0))
            academic_expenditure = float(request.POST.get("academic_expenditure", 0))
            physical_expenditure = float(request.POST.get("physical_expenditure", 0))

            #  Define the max limit based on DecimalField(max_digits=12, decimal_places=2)
            MAX_VALUE = 9999999999.99  

            # Check if any value exceeds the allowed limit
            if any(value > MAX_VALUE for value in [budget, expenditure, total_expenditure, academic_expenditure, physical_expenditure]):
                messages.error(request, "One or more values exceed the allowed limit.")
                return redirect("add_expenditure")

            # Save data if all values are within the limit
            Expenditure.objects.create(
                department=department if department else Department.objects.first(),  # Assign a default department if admin
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

    return render(request, "AddData/add_expenditure.html",{'criterion_id':criterion_id, 'disable_filter': True})

def form5_view(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'Forms/form5.html',{'criterion_id':criterion_id})
def adddata5(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'AddData/adddata5.html',{'criterion_id':criterion_id, 'disable_filter': True})
def form6_view(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'Forms/form6.html',{'criterion_id':criterion_id})
def adddata6(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'AddData/adddata6.html',{'criterion_id':criterion_id,'disable_filter': True})
def form7_view(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'Forms/form7.html',{'criterion_id':criterion_id})
def adddata7(request):
    criterion_id = request.session.get('criterion_id')
    return render(request,'AddData/adddata7.html',{'criterion_id':criterion_id,'disable_filter': True})
def is_admin(user):
    return user.is_staff  # Assuming admin users have is_staff=True
@login_required
def teacher_awards_list(request):
    """Show Teacher Awards with filters (Admins see all, normal users see their own)."""

    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')

    # ✅ Determine records based on user role
    if is_admin(request.user):
        awards = TeacherAward.objects.select_related('teacher__user_profile').all()
        departments = Department.objects.all()

        # ✅ Apply department filter (for Admins)
        if selected_department:
            awards = awards.filter(teacher__user_profile__department__department_code=selected_department)

    else:
        # ✅ Normal users can only see their own awards
        user_profile = get_object_or_404(UserProfile, user=request.user)
        awards = TeacherAward.objects.select_related('teacher__user_profile').filter(
            teacher__user_profile=user_profile
        )

        # ✅ Normal users can only see their own department
        departments = Department.objects.filter(department_code=request.user.userprofile.department.department_code)

    return render(request, 'Forms/teacher_awards.html', {
        "awards": awards,
        "departments": departments, 
        "selected_department": selected_department,
        "criterion_id": criterion_id,
    })


@login_required
def update_teacher_award(request, award_id):
    """Allows only the owner or an admin to edit a teacher award entry."""
    award = get_object_or_404(TeacherAward, id=award_id)

    if not request.user.is_staff and award.teacher.user_profile != request.user.userprofile:
        messages.error(request, "Unauthorized access!")
        return redirect('teacher_awards_list')  

    if request.method == "POST":
        award.teacher_name = request.POST.get("teacher_name")
        award.award_name = request.POST.get("award_name")
        award.recognition_level = request.POST.get("recognition_level")
        award.year_of_award = request.POST.get("year_of_award")
        award.awarding_agency = request.POST.get("awarding_agency")
        award.save()

        messages.success(request, "Teacher award updated successfully!")
        return redirect('teacher_awards_list')  

    messages.error(request, "Invalid request!")
    return redirect('teacher_awards_list')  


@login_required
def delete_teacher_award(request, award_id):
    """Allows only the owner or an admin to delete a teacher award entry."""
    award = get_object_or_404(TeacherAward, id=award_id)

    if not request.user.is_staff and award.teacher.user_profile != request.user.userprofile:
        messages.error(request, "Unauthorized access!")
        return redirect('teacher_awards_list')

    award.delete()
    messages.success(request, "Teacher award deleted successfully!")
    return redirect('teacher_awards_list') 



@login_required
def add_teacher_award(request):
    user = request.user
    criterion_id = request.session.get('criterion_id')

    if request.method == "POST":
        if user.is_superuser:
            teacher_id = request.POST.get("teacher")  
            try:
                teacher = Teacher.objects.get(id=teacher_id)
            except Teacher.DoesNotExist:
                messages.error(request, "Selected teacher does not exist.")
                return redirect("add_teacher_award")
        else:
            try:
                user_profile = UserProfile.objects.get(user=user) 
                teacher = Teacher.objects.get(user_profile=user_profile) 
            except (UserProfile.DoesNotExist, Teacher.DoesNotExist):
                messages.error(request, "Your teacher profile does not exist.")
                return redirect("add_teacher_award")

        # Get form fields
        award_name = request.POST.get("award_name")
        recognition_level = request.POST.get("recognition_level")
        year_of_award = request.POST.get("award_year")
        awarding_agency = request.POST.get("award_agency")

        # Save award entry
        TeacherAward.objects.create(
            teacher=teacher,
            award_name=award_name,
            recognition_level=recognition_level,
            year_of_award=year_of_award,
            awarding_agency=awarding_agency
        )

        messages.success(request, "Teacher Award added successfully!")
        return redirect("teacher_awards_list")  # Redirect to awards list

    teachers = Teacher.objects.all() if user.is_superuser else None 
    return render(request, "AddData/add_teacher_award.html", {"teachers": teachers, "is_admin": user.is_superuser,'criterion_id':criterion_id,'disable_filter': True})
@login_required
def research_grants_list(request):
    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')  # Get department filter from request

    if request.user.is_superuser:
        departments = Department.objects.all()
        grants = ResearchGrant.objects.all()

        # Apply filtering if a department is selected
        if selected_department:
            grants = grants.filter(department__department_code=selected_department)
    else:
        try:
            department = request.user.profile.department  # Get user's department
            departments = [department]  # Convert to list for template
            grants = ResearchGrant.objects.filter(department=department)
        except AttributeError:
            department = None
            departments = []
            grants = ResearchGrant.objects.none()  # Handle missing profile

    return render(request, 'Forms/research_grants_list.html', {
        'grants': grants,
        'criterion_id': criterion_id,
        'departments': departments,
        'selected_department': selected_department  # Pass selected department to template
    })

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def add_research_grant(request):
    criterion_id = request.session.get('criterion_id')
    if request.method == "POST":
        scheme_name = request.POST.get("scheme_name")
        funding_agency = request.POST.get("funding_agency")
        grant_type = request.POST.get("grant_type")
        department_id = request.POST.get("department")  # Ensure this is the correct value
        year_of_award = request.POST.get("year_of_award")
        funds_provided = request.POST.get("funds_provided")
        duration = request.POST.get("duration")
        duration_unit = request.POST.get("duration_unit")
        investigators = request.POST.getlist("investor[]")

        # Determine the correct department
        if request.user.is_superuser:  # Admin can select department manually
            department = get_object_or_404(Department, department_code=department_id)
        else:  # Regular user should have their own department auto-filled
            department = request.user.userprofile.department

        # Create and save ResearchGrant instance
        grant = ResearchGrant.objects.create(
            scheme_name=scheme_name,
            funding_agency=funding_agency,
            grant_type=grant_type,
            department=department,
            year_of_award=year_of_award,
            funds_provided=funds_provided,
            duration=duration,
            duration_unit=duration_unit
        )

        # Save Investigators and link them to the grant
        investigator_objects = [
            Investigator.objects.get_or_create(name=name.strip())[0]
            for name in investigators if name.strip()
        ]
        grant.investigators.set(investigator_objects)

        return redirect("research_grants_list")

    # Fetch all departments for dropdown (Only admins need this)
    departments = Department.objects.all() if request.user.is_superuser else None

    # Get the logged-in user's department
    user_department = None
    if hasattr(request.user, 'userprofile') and request.user.userprofile.department:
        user_department = request.user.userprofile.department

    return render(request, "AddData/add_research_grant.html", {
        "departments": departments,
        "department": user_department,
        'criterion_id':criterion_id , # Auto-filled for users
        'disable_filter': True
    })

def update_grant(request, grant_id):
    if request.method == "POST":
        grant = get_object_or_404(ResearchGrant, id=grant_id)

        try:
            # Basic grant details
            grant.scheme_name = request.POST.get("scheme_name", "").strip()
            grant.funding_agency = request.POST.get("funding_agency", "").strip()
            grant.type = request.POST.get("type", "").strip()

            # Handle department correctly
            department_name = request.POST.get("department", "").strip()
            grant.department = get_object_or_404(Department, department_name=department_name)

            # Convert numerical fields safely
            grant.year_of_award = int(request.POST.get("year_of_award", 0))
            grant.funds_provided = float(request.POST.get("funds_provided", 0))
            grant.duration = int(request.POST.get("duration", 0))
            grant.duration_unit = request.POST.get("duration_unit", "").strip()

            # Handle multiple principal investigators
            investigator_names = request.POST.getlist("principal_investigator[]")  # Fetch all investigators
            grant.investigators.clear()  # Remove old investigators
            
            for name in investigator_names:
                name = name.strip()
                if name:  # Ensure it's not empty
                    investigator, _ = Investigator.objects.get_or_create(name=name)
                    grant.investigators.add(investigator)

            grant.save()
            messages.success(request, "Research grant updated successfully!")
        
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error updating grant: {str(e)}")

    return redirect("research_grants_list")

def delete_grant(request, grant_id):
    grant = get_object_or_404(ResearchGrant, id=grant_id)

    try:
        grant.delete()
        messages.success(request, "Research grant deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting grant: {str(e)}")

    return redirect("research_grants_list")

@login_required
def award_list(request):
    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')
    """List all awards. Admins see all, users see only their department's awards."""
    if request.user.is_superuser:  
        awards = AwardRecognition.objects.all()  # Admin sees all records
    else:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        awards = AwardRecognition.objects.filter(department=user_profile.department)  # Filter by user's department
    
    return render(request, 'Forms/award_list.html', {'awards': awards,'department':selected_department,'criterion_id':criterion_id})

@login_required
def update_award(request, award_id):
    """Update award details (only within the user's department unless admin)."""
    award = get_object_or_404(AwardRecognition, id=award_id)

    # Ensure non-admin users only edit awards from their department
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not request.user.is_superuser and award.department != user_profile.department:
        messages.error(request, "You don't have permission to edit this award.")
        return redirect('award_list')

    if request.method == "POST":
        award.innovation_title = request.POST.get('innovation_title', award.innovation_title)
        award.awardee_name = request.POST.get('awardee_name', award.awardee_name)
        award.awarding_agency = request.POST.get('awarding_agency', award.awarding_agency)
        award.award_year = request.POST.get('award_year', award.award_year)
        award.category = request.POST.get('category', award.category)

        # Handle document upload (if provided)
        if 'document' in request.FILES:
            award.document = request.FILES['document']

        award.save()
        messages.success(request, "Award updated successfully!")

        # Return JSON response for AJAX support
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Award updated successfully!'})

        return redirect('award_list')

    return redirect('award_list')

def award_delete(request, award_id):
    """Delete an award and show a message without redirecting."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    award = get_object_or_404(AwardRecognition, id=award_id)

    try:
        award.delete()
        messages.success(request, "Award deleted successfully!")
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
def add_award(request):
    user = request.user

    if request.method == "POST":
        if "excel_file" in request.FILES:  # Bulk Upload Handling
            excel_file = request.FILES["excel_file"]

            # Validate file format
            if not excel_file.name.endswith(".xlsx"):
                messages.error(request, "Invalid file format. Please upload an Excel file (.xlsx).")
                return redirect("add_award")

            try:
                df = pd.read_excel(excel_file).astype(str).fillna('')  # Convert all values to string & replace NaN

                # Required Columns
                base_required_columns = ["Innovation Title", "Awardee Name", "Awarding Agency", "Year", "Category"]
                required_columns = base_required_columns + ["Department"] if user.is_superuser else base_required_columns

                # Check for Missing Columns
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    messages.error(request, f"Missing columns in Excel: {', '.join(missing_cols)}")
                    return redirect("add_award")

                skipped_rows = []  # Store rows with errors
                for index, row in df.iterrows():
                    department = None

                    # Assign Department
                    if user.is_superuser:
                        department_name = str(row.get("Department", "")).strip()
                        department = Department.objects.filter(name=department_name).first()
                    else:
                        department = get_object_or_404(UserProfile, user=user).department

                    if not department:
                        skipped_rows.append(f"Row {index+2}: Invalid Department ({row.get('Department', 'N/A')})")
                        continue

                    # Validate Award Year
                    try:
                        award_year = int(float(row["Year"]))  # Convert float values like 2022.0 to int
                    except (ValueError, TypeError):
                        skipped_rows.append(f"Row {index+2}: Invalid Year ({row['Year']})")
                        continue

                    # Create Award Entry (Document remains None in bulk upload)
                    AwardRecognition.objects.create(
                        department=department,
                        innovation_title=row["Innovation Title"].strip(),
                        awardee_name=row["Awardee Name"].strip(),
                        awarding_agency=row["Awarding Agency"].strip(),
                        award_year=award_year,
                        category=row["Category"].strip(),
                        document=None,  # Bulk uploads do not support document uploads
                    )

                # Show Skipped Rows
                if skipped_rows:
                    messages.warning(request, "Some rows were skipped due to errors:\n" + "\n".join(skipped_rows))

                messages.success(request, "Awards added successfully from Excel!")
                return redirect("award_list")

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect("add_award")

        else:  # Single Entry Form Submission
            try:
                # Assign Department
                if user.is_superuser:
                    department_code = request.POST.get("department_code")
                    department = get_object_or_404(Department, department_code=department_code)
                else:
                    department = get_object_or_404(UserProfile, user=user).department

                # Get Form Data
                innovation_title = request.POST.get("innovation_title", "").strip()
                awardee_name = request.POST.get("awardee_name", "").strip()
                awarding_agency = request.POST.get("awarding_agency", "").strip()
                award_year = request.POST.get("award_year", "").strip()
                category = request.POST.get("category", "").strip()
                document = request.FILES.get("document")  # Upload Document

                # Validate Required Fields
                if not all([innovation_title, awardee_name, awarding_agency, award_year, category]):
                    messages.error(request, "All fields are required except document.")
                    return redirect("add_award")

                # Validate Year
                try:
                    award_year = int(award_year)
                except ValueError:
                    messages.error(request, "Invalid year format. Please enter a valid numeric year.")
                    return redirect("add_award")

                # Create Award Entry
                AwardRecognition.objects.create(
                    department=department,
                    innovation_title=innovation_title,
                    awardee_name=awardee_name,
                    awarding_agency=awarding_agency,
                    award_year=award_year,
                    category=category,
                    document=document,  # Save uploaded document
                )

                messages.success(request, "Award added successfully!")
                return redirect("award_list")

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect("add_award")

    # Get Departments for Superusers
    departments = Department.objects.all() if user.is_superuser else None
    return render(request, "AddData/add_award.html", {"departments": departments,'disable_filter': True})



@login_required
def patent_list(request):
    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')
    """View to display patents. Superusers see all patents, others see only their department's patents."""
    if request.user.is_superuser:
        patents = Patent.objects.all()
    else:
        patents = Patent.objects.filter(department=request.user.userprofile.department)

    return render(request, 'Forms/patent_list.html', {'patents': patents,'department':selected_department,'criterion_id':criterion_id})

@login_required
def add_patent(request):
    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')
    """Allow users to add patents (restricted to their department)."""
    if request.method == "POST":
        patenter_name = request.POST.get('patenter_name')
        patent_number = request.POST.get('patent_number')
        title = request.POST.get('patent_title')
        award_year = request.POST.get('award_year')
        document = request.FILES.get('document')

        # Assign department from UserProfile
        department = request.user.userprofile.department if not request.user.is_superuser else None

        patent = Patent.objects.create(
            patenter_name=patenter_name,
            patent_number=patent_number,
            title=title,
            award_year=award_year,
            document=document,
            department=department
        )
        messages.success(request, "Patent added successfully!")
        return redirect('patent_list')

    return render(request, 'AddData/add_patent.html',{'department':selected_department,'criterion_id':criterion_id,'disable_filter': True})

@login_required
def edit_patent(request, patent_id):
    """View to edit a patent. Restricts access based on department."""
    patent = get_object_or_404(Patent, id=patent_id)

    if not request.user.is_superuser and patent.department != request.user.userprofile.department:
        messages.error(request, "You do not have permission to edit this patent.")
        return redirect('patent_list')

    if request.method == "POST":
        patent.patenter_name = request.POST.get('patenter_name')
        patent.patent_number = request.POST.get('patent_number')
        patent.title = request.POST.get('title')
        patent.award_year = request.POST.get('award_year')

        if 'document' in request.FILES:
            patent.document = request.FILES['document']

        patent.save()
        messages.success(request, "Patent updated successfully!")
        return redirect('patent_list')

    return render(request, 'edit_patent.html', {'patent': patent})

@login_required
def delete_patent(request, patent_id):
    """View to delete a patent. Restricts access based on department."""
    patent = get_object_or_404(Patent, id=patent_id)

    if not request.user.is_superuser and patent.department != request.user.userprofile.department:
        messages.error(request, "You do not have permission to delete this patent.")
        return redirect('patent_list')

    patent.delete()
    messages.success(request, "Patent deleted successfully!")
    return redirect('patent_list')

@login_required
def phd_list(request):
    criterion_id = request.session.get('criterion_id')
    selected_department = request.GET.get('department', '')
    """Display Ph.D. records based on user role."""
    if request.user.is_superuser:
        phds = PhDAward.objects.all()
    else:
        phds = PhDAward.objects.filter(department=request.user.userprofile.department)
    
    return render(request, "Forms/phd_list.html", {"phds": phds,'criterion_id':criterion_id})

@login_required
def add_phd(request):
    """Add PhD Award - Restrict department for users."""
    departments = Department.objects.all()  # Get list of departments for admins

    if request.method == "POST":
        scholar_name = request.POST.get("scholar_name")
        guides = request.POST.get("guide")
        title = request.POST.get("thesis_title")
        registration_year = request.POST.get("registration_year")
        award_year = request.POST.get("award_year")
        document = request.FILES.get("document")

        if request.user.is_superuser:
            department_code = request.POST.get("department")  # Admin selects department
        else:
            department_code = request.user.userprofile.department.department_code  # Auto-assign for users

        # ✅ Convert department name to a Department instance
        department = get_object_or_404(Department, department_code=department_code)

        # ✅ Now save the PhDAward object
        PhDAward.objects.create(
            scholar_name=scholar_name,
            department=department,  # Assigning Department instance instead of string
            guides=guides,
            title=title,
            registration_year=registration_year,
            award_year=award_year,
            document=document
        )
        messages.success(request, "Ph.D. record added successfully.")
        return redirect("phd_list")

    return render(request, "AddData/phd_form.html", {"departments": departments})

@login_required
def add_demand_ratio(request):
    if request.method == "POST":
        academic_year = request.POST.get("academic_year")
        programme_name = request.POST.get("programme_name")
        programme_code = request.POST.get("programme_code")
        num_seats = request.POST.get("num_seats")
        num_applications = request.POST.get("num_applications")
        num_students_admitted = request.POST.get("num_students_admitted")
        department_code = request.POST.get("department")

        # Convert numeric fields
        try:
            num_seats = int(num_seats)
            num_applications = int(num_applications)
            num_students_admitted = int(num_students_admitted)
        except ValueError:
            return render(request, "AddData/add_demand_ratio.html", {"error": "Invalid input values!"})

        # Restrict department selection for department users
        if not request.user.is_superuser:
            department = request.user.userprofile.department
        else:
            department = Department.objects.get(department_code=department_code)

        # Save the data
        DemandRatio.objects.create(
            academic_year=academic_year,
            programme_name=programme_name,
            programme_code=programme_code,
            num_seats=num_seats,
            num_applications=num_applications,
            num_students_admitted=num_students_admitted,
            department=department
        )

        return redirect("demand_ratio_list")  # Redirect to the list page after saving

    # Generate academic year options in yyyy-yyyy format
    from datetime import datetime
    current_year = datetime.now().year
    academic_years = [f"{y}-{y+1}" for y in range(2000, current_year + 1)]

    departments = Department.objects.all() if request.user.is_superuser else [request.user.userprofile.department]

    return render(request, "AddData/add_demand_ratio.html", {"academic_years": academic_years, "departments": departments})

@login_required
def demand_ratio_list(request):
    """
    Display a list of Demand Ratio records with department-level restrictions.
    Superusers can view all records, while department users see only their department's data.
    """
    # Check if the user is a superuser
    if request.user.is_superuser:
        # Superusers can view all data
        records = DemandRatio.objects.all()
    else:
        # Department users can only view their department's data
        if hasattr(request.user, "userprofile") and hasattr(request.user.userprofile, "department"):
            user_department = request.user.userprofile.department
            records = DemandRatio.objects.filter(department=user_department)
        else:
            # If the user has no associated department, return an empty queryset
            records = DemandRatio.objects.none()

    # Apply filters if provided
    programme_name = request.GET.get('programme_name', '').strip()
    programme_code = request.GET.get('programme_code', '').strip()
    year_from = request.GET.get('year_from', '').strip()
    year_to = request.GET.get('year_to', '').strip()

    if programme_name:
        records = records.filter(programme_name__icontains=programme_name)

    if programme_code:
        records = records.filter(programme_code__icontains=programme_code)

    if year_from and year_to:
        records = records.filter(academic_year__gte=year_from, academic_year__lte=year_to)
    elif year_from:
        records = records.filter(academic_year__gte=year_from)
    elif year_to:
        records = records.filter(academic_year__lte=year_to)

    context = {
        'records': records,
    }

    return render(request, 'Forms/demand_ratio_list.html', context)

def admitted_student_list(request):
    return render(request,'Forms/admited_students.html')
def add_admitted_student(request):
    return render(request,'AddData/add_admitted_student.html')
def teacher_serving_post_list(request):
    return render(request,'Forms/teacher_post.html')
def add_teacher_serving_post(request):
    return render(request,'AddData/add_teacher_post.html')
def teacher(request):
    return render(request,'Forms/teacher.html')
def add_teacher(request):
    return render(request,'AddData/add_teacher.html')
def against_sanctioned_post(request):
    return render(request,'Forms/against_sanctioned_post.html')
def add_against_sanctioned_post(request):
    return render(request,'AddData/add_against_sanctioned_post.html')
def e_governance(request):
    return render(request,"Forms/e_governance.html")
def add_e_governance(request):
    return render(request,"AddData/add_e_governance.html")
def conference(request):
    return render(request,"Forms/conference.html")
def add_conference(request):
    return render(request,"AddData/add_conference.html")
def training_record(request):
    return render(request,"Forms/training_record.html")
def add_training_record(request):
    return render(request,"AddData/add_training_record.html")
def faculty_development_program(request):
    return render(request,"Forms/faculty_development_program.html")
def add_faculty_development_program(request):
    return render(request,"AddData/add_faculty_development_program.html")
def grant_record(request):
    return render(request,"Forms/grant.html")
def add_grant_record(request):
    return render(request,"AddData/add_grand.html")
def quality_assurance(request):
    return render(request,"Forms/quality_assurance.html")
def add_quality_assurance(request): 
    return render(request,"AddData/add_quality_assurance.html")
def scholarship_list(request):
    return render(request,"Forms/scholarship.html")
def add_scholarship(request):
    return render(request,"AddData/add_scholarship.html")
def career_counseling(request):
    return render(request,"Forms/career_counseling.html")
def add_career_counseling(request):
    return render(request,"AddData/add_career_counseling.html")