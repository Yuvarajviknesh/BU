from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import LibraryResource, UserProfile,Department

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
@login_required
def form_view(request):
    return render(request,'Forms/Form1.html')
@login_required
def form2_view(request):
    return render(request,'Forms/Form2.html')
@login_required
def form3_view(request):
    return render(request,'Forms/Form3.html')
@login_required
def form4_view(request):
    return render(request,'Forms/Form4.html')
@login_required
def addData4_view(request):
    return render(request,'AddData/addData4.html')
@login_required
def addData1_view(request):
    return render(request,'AddData/addData1.html')
@login_required
def addData2_view(request):
    return render(request,'AddData/addData2.html')
@login_required
def addData3_view(request):
    return render(request,'AddData/addData3.html')
@login_required
def dataView1_view(request):
    return render(request,'viewData/viewData.html')


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
        resources = LibraryResource.objects.filter(department__name="Library")  # Library users see only library data
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

        # Get the Library department instance
        try:
            library_department = Department.objects.get(name="Library")  # Ensure the department exists
        except Department.DoesNotExist:
            messages.error(request, "Library department not found.")
            return redirect("add_library_resource")

        # Convert expenditure values to float or int
        try:
            expenditure_journals = float(expenditure_journals)
            expenditure_other_resources = float(expenditure_other_resources)
            total_expenditure = float(total_expenditure)
        except ValueError:
            messages.error(request, "Invalid expenditure values entered.")
            return redirect("add_library_resource")

        # Save resource data in the database
        resource = LibraryResource.objects.create(
            academic_year=academic_year,
            resource_name=resource_name,
            expenditure_journals=expenditure_journals,
            expenditure_other_resources=expenditure_other_resources,
            total_expenditure=total_expenditure,
            document=document,
            department=library_department  # Assigning the department here
        )

        messages.success(request, "Library resource added successfully!")
        return redirect("library_resources")  # Redirect to the resource listing page

    return render(request, "AddData/add_library_resource.html")

def delete_library_resource(request, id):
    resource = get_object_or_404(LibraryResource, id=id)
    resource.delete()
    return redirect('library_resources')  # Redirect to the main page after deletion