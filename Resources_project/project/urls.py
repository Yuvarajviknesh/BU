# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),          # Home page
    path("login/", views.login_view, name="login"),  # Login page
    path("", views.login_view, name="login"),  # Login page
    path("logout/", views.logout_view, name="logout"),  # Logout page
    path('library-resources/', views.library_resources, name='library_resources'),
    path('update-resource/<int:resource_id>/', views.update_library_resource, name='update_library_resource'),
    path("add-library-resource/", views.add_library_resource, name="add_library_resource"),
    path('library-resource/<int:id>/delete/', views.delete_library_resource, name='delete_library_resource'),
    path("facilities/", views.ict_facility_list, name="ict_facility_list"),
    path("facilities/<int:facility_id>/update/", views.update_facility, name="update_facility"),
    path("facilities/<int:facility_id>/delete/", views.delete_ict_facility, name="delete_facility"),
    path("add-ict-facility/", views.add_ict_facility, name="add_ict_facility"),
    path('econtent/', views.show_econtent, name='show_econtent'),
    path('econtent/<int:record_id>/update/', views.edit_econtent, name='edit_econtent'),
    path('econtent/<int:record_id>/delete/', views.delete_econtent, name='delete_econtent'),
    path('econtents/add/', views.add_econtent, name='add_econtent'),
    path('expenditure/', views.expenditure_list, name='expenditure_list'),  # View all records
    path('expenditure/add/', views.add_expenditure, name='add_expenditure'),  # Add a new record
    path('expenditure/edit/<int:record_id>/', views.edit_expenditure, name='update_expenditure'),  # Edit a record
    path('expenditure/delete/<int:record_id>/', views.delete_expenditure, name='delete_expenditure'),  # Delete a record
]



