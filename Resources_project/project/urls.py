from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('create_teacher_profile/', views.create_teacher_profile, name='create_teacher_profile'),
    path("user-login/", views.user_login, name="user_login"),
    path("", views.user_login, name="login"),  
    path("logout/", views.logout_view, name="logout"),  
    path('criteria/<int:criterion_number>/', views.criterion_page, name='criterion_page'),
    path("department-dashboard/", views.department_dashboard, name="department_dashboard"),
    path("staff-dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("scholar-dashboard/", views.scholar_dashboard, name="scholar_dashboard"),
    path('admin/reports/', views.admin_report_generator, name='generator'),
    
    

    #admin block
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    

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
      path('phd/edit/<int:phd_id>/', views.edit_phd, name='edit_phd'),  # Edit PhD record
      path('phd/delete/<int:phd_id>/', views.delete_phd, name='delete_phd'),  
      path('phd/view/<int:phd_id>/', views.view_phd, name='view_phd'),
      path('phd/download-pdf/<int:phd_id>/', views.download_phd_pdf, name='download_phd_pdf'),
      
      # Research Paper
      path('research-papers/', views.view_research_papers, name='view_research_papers'),
      path('research-papers/add/', views.add_research_paper, name='add_research_paper'),
      path('research-papers/edit/<int:paper_id>/', views.edit_research_paper, name='edit_research_paper'),
      path('research-papers/delete/<int:paper_id>/', views.delete_research_paper, name='delete_research_paper'),
      path('research-papers/view/<int:paper_id>/', views.view_research_paper, name='view_research_paper'),
      path('research-papers/download-pdf/<int:paper_id>/', views.download_research_paper_pdf, name='download_research_paper_pdf'),
    
     #book 
      
      path('book-chapters/', views.view_book_chapters, name='view_book_chapters'),

    # Add a new book/chapter
      path('book-chapters/add/', views.add_book_chapter, name='add_book_chapter'),

    # Edit an existing book/chapter
      path('book-chapters/edit/<int:book_id>/', views.edit_book_chapter, name='edit_book_chapter'),

    # Delete a book/chapter
       path('book-chapters/delete/<int:book_id>/', views.delete_book_chapter, name='delete_book_chapter'),
        path('book-chapters/view/<int:book_id>/', views.view_book_chapter_details, name='view_book_chapter_details'),
        path('book-chapters/download-pdf/<int:book_id>/', views.download_book_chapter_pdf, name='download_book_chapter_pdf'),
      #demand ratio
       path('demand-ratio/', views.demand_ratio_list, name='demand_ratio_list'),
       path('demand-ratio/add/', views.add_demand_ratio, name='add_demand_ratio'),
      path('demand-ratio/edit/<int:record_id>/', views.edit_demand_ratio, name='edit_demand_ratio'),
       path('demand-ratio/delete/<int:record_id>/', views.delete_demand_ratio, name='delete_demand_ratio'),
       path('demand-ratio/view/<int:record_id>/', views.view_demand_ratio_details, name='view_demand_ratio_details'),
      path('demand-ratio/download-pdf/<int:record_id>/', views.download_demand_ratio_pdf, name='download_demand_ratio_pdf'),

      #admitted students
      path('admitted-students/', views.admitted_student_list, name='admitted_students_list'),
      path('admitted-students/add/', views.add_admitted_student, name='add_admitted_student'),
     path('admitted-student/edit/<int:record_id>/', views.edit_admitted_student, name='edit_admitted_student'),
      path('admitted-student/delete/<int:record_id>/', views.delete_admitted_student, name='delete_admitted_student'),
      path('admitted-student/view/<int:record_id>/', views.view_admitted_student_details, name='view_admitted_student_details'),
    path('admitted-student/download-pdf/<int:record_id>/', views.download_admitted_student_pdf, name='download_admitted_student_pdf'),
      #teacher serving post
      path('teacher-serving-post/', views.teacher_serving_post_list, name='teacher_serving_post_list'),
      path('teacher-serving-post/add/', views.add_teacher_serving_post, name='add_teacher_serving_post'),
       path('teacher-serving-post/edit/<int:record_id>/', views.edit_teacher_serving_post, name='edit_teacher_serving_post'),
      path('teacher-serving-post/delete/<int:record_id>/', views.delete_teacher_serving_post, name='delete_teacher_serving_post'),

      #teacher 
      path('full-time-teacher/list/', views.full_time_teacher_list, name='full_time_teacher_list'),
      path('teachers/add/', views.add_teacher, name='add_teacher'),
      path('teachers/edit/<int:record_id>/', views.edit_teacher, name='edit_teacher'),
       path('teachers/delete/<int:record_id>/', views.delete_teacher, name='delete_teacher'),
     # aganist santioned post
     path('teacher-sanctioned-post-list/', views.teacher_sanctioned_post_list, name='teacher_sanctioned_post_list'),
      path('against-sanctioned-post/add/', views.add_against_sanctioned_post, name='add_against_sanctioned_post'),
          # Edit record route
    path('edit-teacher/<int:post_id>/', views.edit_teacher_against_sanctioned_post, name='edit_teacher_against_sanctioned_post'),

    # Delete record route
    path('delete-teacher/<int:post_id>/', views.delete_teacher_against_sanctioned_post, name='delete_teacher_against_sanctioned_post'),


    #conference
    path('e-governance/', views.e_governance, name='e_governance_list'),
    path('e-governance/add/', views.add_e_governance, name='add_e_governance'),
    path('conference/', views.conference, name='conference_list'),
    path('conference/add/', views.add_conference, name='add_conference'),
    path('training_record/', views.training_record, name='training_record_list'),
    path('training_record/add/', views.add_training_record, name='add_training_record'),
    path('faculty_development/', views.faculty_development_program, name='faculty_development_list'),
    path('faculty_development/add/', views.add_faculty_development_program, name='add_faculty_development'),
    path('grant/',views.grant_record,name='grant_record'),
    path('grant/add/',views.add_grant_record,name='add_grant_record'),
    path('quality_assurance/',views.quality_assurance,name='quality_assurance_list'),
    path('quality_assurance/add/',views.add_quality_assurance,name='add_quality_assurance'),
    path('scholarship/',views.scholarship_list,name='scholarship_list'),
    path('scholarship/add/',views.add_scholarship,name='add_scholarship'),
    path('career_counseling/',views.career_counseling,name='career_counseling_list'),
    path('career_counseling/add/',views.add_career_counseling,name='add_career_counseling'),
    path('program_list/',views.programme_list,name='program_list'),
    path('program_list/add/',views.add_programme,name='add_program_list'),
    path("edit-programme/<int:programme_id>/", views.edit_programme_view, name="edit_programme"),
    path("delete-programme/<int:programme_id>/", views.delete_programme_view, name="delete_programme"),
    path("download-excel/", views.download_excel, name="download_excel"),
    path("download-pdf/", views.download_pdf, name="download_pdf"),
    path('programme/<int:programme_id>/pdf/', views.download_programme_pdf, name='download_programme_pdf'),
    path('programme/<int:id>/', views.view_programme, name='view_programme'),
    path('courses/', views.view_courses, name='view_courses'),
    path('courses/download/', views.view_courses, name='course_downloads'),
   path('courses/download_excel/', views.view_courses, {'download': 'excel'}, name='download_excel'),
   path('courses/download_pdf/', views.view_courses, {'download': 'pdf'}, name='download_pdf'),
     path("courses/add/", views.add_course, name="add_course"),
     path("courses/edit/<int:course_id>/", views.edit_course, name="edit_course"),
     path("courses/delete/<int:course_id>/", views.delete_course_view, name="delete_course"),
     path("courses/<int:course_id>/download/", views.download_course_pdf, name="download_course_pdf"),
    path("courses/<int:course_id>/", views.course_detail_view, name="course_detail"),
    path("value-added-courses/", views.value_added_course, name="value_added_courses"),
    path("value-added-courses/add/", views.add_value_added_course, name="add_value_added_course"),
    path("value-added/edit/<int:course_id>/", views.edit_value_added_course, name="edit_value_added_course"),
    path("value-added/delete/<int:course_id>/", views.delete_value_added_course, name="delete_value_added_course"),
    path("projects/", views.student_project_list_view, name="student_project_list"),
    path("projects/add/", views.add_student_project_view, name="add_student_project"),
    path("projects/edit/<int:project_id>/", views.edit_student_project_view, name="edit_student_project"),
    path("projects/delete/<int:project_id>/", views.delete_student_project_view, name="delete_student_project"),
]
