from django.contrib import admin

# Register your models here.
from .models import (
    Asset,
    AssetError,
    AssetLink,
    Block,
    Column,
    ColumnLink,
    GithubInstallation,
    Notebook,
    Resource,
    Workspace,
)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "is_staff", "is_active"]
    list_filter = ["email", "is_staff", "is_active"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Asset)
admin.site.register(Column)
admin.site.register(AssetLink)
admin.site.register(ColumnLink)
admin.site.register(Resource)
admin.site.register(AssetError)
admin.site.register(Block)
admin.site.register(Notebook)
admin.site.register(GithubInstallation)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Workspace)
