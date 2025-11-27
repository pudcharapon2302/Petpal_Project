from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from .views import Landing_Page, account_delete, add_comment, adoption_requests_list, chat_api, delete_post, generate_poster, my_posts_list, pet_add, pet_create, pet_delete, pet_detail, pet_edit, pet_report_edit, profile_page, profile_update, register , adoption_list_view, lost_list_view, pet_report_create, renew_post , report_select_category , foundation_list_view , cat_list_view, dog_list_view, post_detail_view, send_adoption_request, chat_room, toggle_post_status, train_ai_basic, update_adoption_status , ai_chat_page

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
    path("accounts/pets/<int:pk>/edit/", pet_edit, name="pet_edit"),
    path("accounts/pets/<int:pk>/delete/", pet_delete, name="pet_delete"),

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

    # Manage Posts
    path('my-posts/', my_posts_list, name='my_posts_list'),
    path('my-posts/<int:pk>/toggle/', toggle_post_status, name='toggle_post_status'),
    path('my-posts/<int:pk>/delete/', delete_post, name='delete_post'),
    path('my-posts/<int:pk>/edit/', pet_report_edit, name='pet_report_edit'),
    path('my-posts/<int:pk>/renew/', renew_post, name='renew_post'),
    path('post/<int:pk>/poster/', generate_poster, name='generate_poster'),

    # AI Chat Page
    path('ai-chat/', ai_chat_page, name='ai_chat_page'),
    path('api/chat/', chat_api, name='chat_api'),
    path('admin/train-ai/', train_ai_basic, name='train_ai'),

    # Comments
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),

    # --- Password Reset URLs ---
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='myapp/registration/password_reset_form.html',
             email_template_name='myapp/registration/password_reset_email.html',
             html_email_template_name='myapp/registration/password_reset_email.html',
             subject_template_name='myapp/registration/password_reset_subject.txt'
         ),
         name='password_reset'),

    # 2. แจ้งว่าส่งเมลแล้ว
    path('accounts/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='myapp/registration/password_reset_done.html'),
         name='password_reset_done'),

    # 3. ลิงก์จากอีเมล (ตั้งรหัสใหม่) - สำคัญ! ชื่อตัวแปรต้องเป๊ะ
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='myapp/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # 4. เสร็จสิ้น
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='myapp/registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
