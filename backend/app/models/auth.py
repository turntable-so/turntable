import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.db import models

from app.services.storage_backends import PublicMediaStorage
from app.utils.fields import encrypt


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def current_workspace(self):
        return self.workspaces.first()

    def __str__(self):
        return self.email


class Workspace(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=255
    )
    name = models.CharField(max_length=1000)
    icon_url = models.URLField(blank=True, null=True)
    icon_file = models.ImageField(
        storage=PublicMediaStorage(), upload_to="assets/icons/", blank=True, null=True
    )
    users = models.ManyToManyField(User, related_name="workspaces")

    class Meta:
        permissions = [
            ("manage_workspace", "Can manage workspace"),
        ]

    def _create_default_workspace_group(self):
        manage_workspace_perm = Permission.objects.get(codename="manage_workspace")
        admin_group = WorkspaceGroup.objects.create(name="Admin", workspace=self)
        member_group = WorkspaceGroup.objects.create(name="Member", workspace=self)

        admin_group.permissions.add(manage_workspace_perm)
        admin_group.save()
        member_group.save()

    def add_admin(self, user: User):
        self.users.add(user)

        # remove if in another group
        member_group = self.groups.get(name="Member")
        member_group.users.remove(user)
        member_group.save()

        admin_group = self.groups.get(name="Admin")
        admin_group.users.add(user)
        admin_group.save()

    def add_member(self, user: User):
        self.users.add(user)

        # remove if in another group
        admin_group = self.groups.get(name="Admin")
        admin_group.users.remove(user)
        admin_group.save()

        admin_group = self.groups.get(name="Member")
        admin_group.users.add(user)
        admin_group.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self._create_default_workspace_group()

    def __str__(self) -> str:
        return self.name


class WorkspaceGroup(models.Model):
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="groups"
    )
    permissions = models.ManyToManyField(Permission, blank=True)
    users = models.ManyToManyField(User, related_name="workspace_groups")

    def __str__(self) -> str:
        return f"{self.name} - {self.workspace.name}"


class WorkspaceSetting(models.Model):
    name = models.CharField(max_length=255)
    secret_value = encrypt(models.CharField(max_length=512, null=True))
    plaintext_value = models.CharField(max_length=512, null=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="settings"
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["name", "workspace"]
            ),  # Composite index on 'name' and 'workspace'
        ]
