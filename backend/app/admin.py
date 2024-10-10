from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import (
    Asset,
    AssetError,
    AssetLink,
    Block,
    Column,
    ColumnLink,
    Notebook,
    Resource,
    User,
    Workspace,
)


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
admin.site.register(User, CustomUserAdmin)
admin.site.register(Workspace)
