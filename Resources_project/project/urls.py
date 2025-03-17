from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),  # Home page
    path("user-login/", views.user_login, name="user_login"),
    path("", views.user_login, name="login"),  
    path("logout/", views.logout_view, name="logout"),  
    path('criteria/<int:criterion_number>/', views.criterion_page, name='criterion_page'),
    path("department-dashboard/", views.department_dashboard, name="department_dashboard"),
    path("staff-dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("scholar-dashboard/", views.scholar_dashboard, name="scholar_dashboard"),

    

    # 📚 Library Resources
    path("library-resource/", views.library_resources, name="library_resources"),
    path("library-resource/add/", views.add_library_resource, name="add_library_resource"),
    path("library-resource/edit/<int:resource_id>/", views.update_library_resource, name="update_library_resource"),
    path("library-resource/delete/<int:resource_id>/", views.delete_library_resource, name="delete_library_resource"),
    path('library-resources/download/', views.download_library_resources_excel, name='download_library_resources_excel'),
    path('library-resource/<int:resource_id>/', views.library_resource_detail, name='library_resource_detail'),
    path('library-resource/<int:resource_id>/download/', views.download_library_resource_pdf, name='download_library_resource_pdf'),


    # 🏢 Facilities
    path("facilities/", views.ict_facility_list, name="ict_facility_list"),
    path("facilities/add/", views.add_ict_facility, name="add_ict_facility"),
    path("facilities/edit/<int:facility_id>/", views.update_facility, name="update_facility"),
    path("facilities/delete/<int:facility_id>/", views.delete_ict_facility, name="delete_facility"),
    path("facility/<int:facility_id>/", views.facility_detail, name="facility_detail"),
    path("download/pdf/<int:facility_id>/", views.download_facility_pdf, name="download_facility_pdf"),
     path('download-ict-facilities/', views.download_ict_facilities, name='download_ict_facilities'),

    # 🎥 E-Content
    path("econtent/", views.show_econtent, name="show_econtent"),
    path("econtent/add/", views.add_econtent, name="add_econtent"),
    path("econtent/edit/<int:record_id>/", views.edit_econtent, name="edit_econtent"),
    path("econtent/delete/<int:record_id>/", views.delete_econtent, name="delete_econtent"),
    path("download_econtent_excel/", views.download_econtent_excel, name="download_econtent_excel"),
    path("econtent/<int:record_id>/", views.view_econtent_detail, name="econtent_detail"),
    path("econtent/download_pdf/<int:econtent_id>/", views.download_econtent_pdf, name="download_econtent_pdf"),



    # 💵 Expenditure
    path("expenditure/", views.expenditure_list, name="expenditure_list"),
    path("expenditure/add/", views.add_expenditure, name="add_expenditure"),
    path("expenditure/edit/<int:record_id>/", views.edit_expenditure, name="update_expenditure"),
    path("expenditure/delete/<int:record_id>/", views.delete_expenditure, name="delete_expenditure"),
    path('download/expenditures/', views.download_expenditure_excel, name='download_expenditure_excel'),
    path('expenditure/<int:expenditure_id>/', views.view_expenditure_detail, name='view_expenditure'),
    path('download/expenditure/<int:expenditure_id>/', views.download_expenditure_pdf, name='download_expenditure_pdf'),

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

      #demand ratio
       path('demand-ratio/', views.demand_ratio_list, name='demand_ratio_list'),
       path('demand-ratio/add/', views.add_demand_ratio, name='add_demand_ratio'),

      #admitted students
      path('admitted-students/', views.admitted_student_list, name='admitted_students_list'),
      path('admitted-students/add/', views.add_admitted_student, name='add_admitted_student'),
      #teacher serving post
      path('teacher-serving-post/', views.teacher_serving_post_list, name='teacher_serving_post_list'),
      path('teacher-serving-post/add/', views.add_teacher_serving_post, name='add_teacher_serving_post'),

      #teacher 
      path('teachers/', views.teacher, name='teacher_list'),
      path('teachers/add/', views.add_teacher, name='add_teacher'),
     # aganist santioned post
     path('against-sanctioned-post/', views.against_sanctioned_post, name='against_sanctioned_post_list'),
      path('against-sanctioned-post/add/', views.add_against_sanctioned_post, name='add_against_sanctioned_post'),
]
