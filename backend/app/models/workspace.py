import uuid

from django.contrib.auth.models import (
    Permission,
)
from django.contrib.postgres.fields import ArrayField
from django.db import models

from app.models.user import User
from app.services.storage_backends import PublicMediaStorage


def generate_short_uuid():
    return uuid.uuid4().hex[:6]


class Workspace(models.Model):
    id = models.CharField(
        primary_key=True, max_length=255, default=generate_short_uuid, editable=False
    )
    name = models.CharField(max_length=1000)
    icon_url = models.URLField(blank=True, null=True)
    icon_file = models.ImageField(
        storage=PublicMediaStorage(), upload_to="assets/icons/", blank=True, null=True
    )
    users = models.ManyToManyField(User, related_name="workspaces")
    assets_exclude_name_contains = ArrayField(
        models.CharField(max_length=255), default=list
    )

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

    def get_dbt_dev_details(self):
        # import here to avoid circular import
        from app.models.resources import DBTResource

        # get dev environment options in order of preference
        return DBTResource.get_development_dbtresource(self.id)

    @property
    def member_count(self):
        return self.users.count()

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
