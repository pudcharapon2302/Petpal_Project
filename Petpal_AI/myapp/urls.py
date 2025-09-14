from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import Landing_Page, register

urlpatterns = [
    path('', Landing_Page, name='landing'),
    path("accounts/register/", register, name="register"),

    # Login / Logout
    path("accounts/login/",  LoginView.as_view(template_name="myapp/registration/login.html"), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),

    path("profile/", views.profile_page, name="profile"),
    path("profile/update/", views.profile_update, name="profile_update"),
    path("pets/create/", views.pet_create, name="pet_create"),
]
