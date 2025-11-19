from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import Landing_Page, account_delete, adoption_requests_list, pet_add, pet_create, pet_delete, pet_detail, pet_edit, profile_page, profile_update, register , adoption_list_view, lost_list_view, pet_report_create , report_select_category , foundation_list_view , cat_list_view, dog_list_view, post_detail_view, send_adoption_request, chat_room, update_adoption_status 

urlpatterns = [
    path('', Landing_Page, name='landing'),
    path("accounts/register/", register, name="register"),

    # Login / Logout
    path("accounts/login/",  LoginView.as_view(template_name="myapp/registration/login.html"), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),

    # profile
    path("accounts/profile/", profile_page, name="profile"),
    path("accounts/delete/", account_delete, name="account_delete"),
    path("accounts/profile/update/", profile_update, name="profile_update"),
    path("accounts/pets/create/", pet_create, name="pet_create"),

    # Pet Profile
    path("accounts/pets/add/",    pet_add,    name="pet_add"),
    path("accounts/pets/<int:pk>/", pet_detail, name="pet_detail"),

    # Pet edit
    path("accounts/pets/<int:pk>/edit/", pet_edit, name="pet_edit"),      # ✅ แก้ไข
    path("accounts/pets/<int:pk>/delete/", pet_delete, name="pet_delete"),# ✅ ลบ

    # Adoption & Lost List
    path('pet/adoptions/', adoption_list_view, name='adoption_list'),
    path('pet/lost/', lost_list_view, name='lost_list'),

    # Pet report
    path('report/select/', report_select_category, name='report_select_category'),
    path('report/create/<str:post_type>/', pet_report_create, name='pet_report_create'),

    #Foundations
    path('contact/', foundation_list_view, name='contact_list'),

    #Cats , Dogs Pages
    path('pets/cats/', cat_list_view, name='cat_list'),
    path('pets/dogs/', dog_list_view, name='dog_list'),
    path('post/<int:pk>/', post_detail_view, name='post_detail'),

    # Send adoption request
    path('post/<int:pk>/adopt/', send_adoption_request, name='send_adoption_request'),
    path('notifications/requests/', adoption_requests_list, name='adoption_requests_list'),

    # Chat messages
    path('chat/<int:request_id>/', chat_room, name='chat_room'),
    path('chat/<int:request_id>/action/<str:action>/', update_adoption_status, name='update_adoption_status'),

    
]
