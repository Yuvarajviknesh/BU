from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),  # Home page
    path("login/", views.login_view, name="login"),  
    path("", views.login_view, name="login"),  
    path("logout/", views.logout_view, name="logout"),  
    path('criteria/<int:criterion_number>/', views.criterion_page, name='criterion_page'),
    

    # 📚 Library Resources
    path("library-resource/", views.library_resources, name="library_resources"),
    path("library-resource/add/", views.add_library_resource, name="add_library_resource"),
    path("library-resource/edit/<int:resource_id>/", views.update_library_resource, name="update_library_resource"),
    path("library-resource/delete/<int:resource_id>/", views.delete_library_resource, name="delete_library_resource"),

    # 🏢 Facilities
    path("facilities/", views.ict_facility_list, name="ict_facility_list"),
    path("facilities/add/", views.add_ict_facility, name="add_ict_facility"),
    path("facilities/edit/<int:facility_id>/", views.update_facility, name="update_facility"),
    path("facilities/delete/<int:facility_id>/", views.delete_ict_facility, name="delete_facility"),

    # 🎥 E-Content
    path("econtent/", views.show_econtent, name="show_econtent"),
    path("econtent/add/", views.add_econtent, name="add_econtent"),
    path("econtent/edit/<int:record_id>/", views.edit_econtent, name="edit_econtent"),
    path("econtent/delete/<int:record_id>/", views.delete_econtent, name="delete_econtent"),

    # 💵 Expenditure
    path("expenditure/", views.expenditure_list, name="expenditure_list"),
    path("expenditure/add/", views.add_expenditure, name="add_expenditure"),
    path("expenditure/edit/<int:record_id>/", views.edit_expenditure, name="update_expenditure"),
    path("expenditure/delete/<int:record_id>/", views.delete_expenditure, name="delete_expenditure"),

    # 📝 Forms
    path("form1/", views.form1_view, name="form1"),
    path("adddata1/", views.adddata1, name="adddata1"),
    path("form2/", views.form2_view, name="form2"),
    path("adddata2/", views.adddata2, name="adddata2"),
]
