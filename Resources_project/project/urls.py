# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),          # Home page
    path("login/", views.login_view, name="login"),  # Login page
    path("", views.login_view, name="login"),  # Login page
    path("logout/", views.logout_view, name="logout"),  # Logout page
    path("form/", views.form_view, name="form"),  
    path("form2/", views.form2_view, name="form2"),  
    path("form3/", views.form3_view, name="form3"),  
    path("form4/", views.form4_view, name="form4"),  
    path("adddata4/", views.addData4_view, name="addData4"),  
    path("adddata1/", views.addData1_view, name="addData1"),  
    path("adddata2/", views.addData2_view, name="addData2"),  
    path("adddata3/", views.addData3_view, name="addData3"),  
    path("dataview1/", views.dataView1_view, name="dataView1"),  
    path('library-resources/', views.library_resources, name='library_resources'),
    path('update-resource/<int:resource_id>/', views.update_library_resource, name='update_library_resource'),
    path("add-library-resource/", views.add_library_resource, name="add_library_resource"),
    path('library-resource/<int:id>/delete/', views.delete_library_resource, name='delete_library_resource'),
]



