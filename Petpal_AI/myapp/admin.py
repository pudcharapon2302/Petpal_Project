from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User , Profile, Pet

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Extra info", {"fields": ("phone", "address", "user_status", "role")}),
    )
    list_display = ("username", "email", "phone", "address", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "role", "user_status")
    search_fields = ("username", "email", "phone")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")
    search_fields = ("user__username", "user__email")

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "birth_date", "created_at")
    list_filter = ("birth_date",)
    search_fields = ("name", "owner__username", "owner__email")