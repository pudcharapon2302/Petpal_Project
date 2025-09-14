from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone", "address", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone", "address", "role", "user_status")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone", "address", "role", "user_status")}),
    )
