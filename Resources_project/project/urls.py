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
    path("form5/", views.form5_view, name="form5"),
    path("adddata5/", views.adddata5, name="adddata5"),     
     path("form6/", views.form6_view, name="form6"),
    path("adddata6/", views.adddata6, name="adddata6"),        
     path("form7/", views.form7_view, name="form7"),
    path("adddata7/", views.adddata7, name="adddata7"),    

    #awards
    path('teacher-awards/', views.teacher_awards_list, name='teacher_awards_list'),
    path('teacher-awards/update/<int:award_id>/', views.update_teacher_award, name='update_teacher_award'),
    path('teacher-awards/delete/<int:award_id>/', views.delete_teacher_award, name='delete_teacher_award'),    
    path('add-teacher-award/', views.add_teacher_award, name='add_teacher_award'),     

    #research_grands
    path('research-grants/', views.research_grants_list, name='research_grants_list'),
     path("add-research-grant/", views.add_research_grant, name="add_research_grant"),
     path('research-grants/update/<int:grant_id>/', views.update_grant, name='update_grant'),
     path("grant/delete/<int:grant_id>/", views.delete_grant, name="delete_grant"),

     #awards
     path('awards/', views.award_list, name='award_list'),
     path('awards/update/<int:award_id>/', views.update_award, name='update_award'),
     path('awards/delete/<int:award_id>/', views.award_delete, name='award_delete'),
     path('awards/add/', views.add_award, name='add_award'),

     #patents
       path('patents/', views.patent_list, name='patent_list'),
       path('patents/edit/<int:patent_id>/', views.edit_patent, name='edit_patent'),
       path('patents/delete/<int:patent_id>/', views.delete_patent, name='delete_patent'),
       path('patents/add/', views.add_patent, name='add_patent'),
     #phds
      path("phds/", views.phd_list, name="phd_list"),
      path("phds/add/", views.add_phd, name="add_phd"),
                                       
]
