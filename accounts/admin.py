# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "phone_number", "full_name", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ("email", "phone_number")
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "phone_number", "password")}),
        (_("Personal info"), {"fields": ("full_name",)}),
        (_("Permissions"), {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone_number", "password1", "password2", "is_staff", "is_active")}
        ),
    )


admin.site.register(User, CustomUserAdmin)

