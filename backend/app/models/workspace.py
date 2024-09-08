import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.db import models

from app.services.storage_backends import PublicMediaStorage
from app.models.user import User
from app.utils.fields import encrypt

def default_workspace_config():
    return {'ai_provider': 'none'}


class Workspace(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=255
    )
    name = models.CharField(max_length=1000)
    icon_url = models.URLField(blank=True, null=True)
    icon_file = models.ImageField(
        storage=PublicMediaStorage(), upload_to="assets/icons/", blank=True, null=True
    )
    config = models.JSONField(default=default_workspace_config)
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

    @property
    def member_count(self):
        return self.users.count()

    def __str__(self) -> str:
        return self.name

class WorkspaceSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, null=True, related_name="settings")
    openai_api_key = encrypt(models.TextField(null=True))
    anthropic_api_key = encrypt(models.TextField(null=True))

class WorkspaceGroup(models.Model):
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="groups"
    )
    permissions = models.ManyToManyField(Permission, blank=True)
    users = models.ManyToManyField(User, related_name="workspace_groups")

    def __str__(self) -> str:
        return f"{self.name} - {self.workspace.name}"
