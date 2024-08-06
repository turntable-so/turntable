import pytest
from app.models import User, Workspace

pytestmark = pytest.mark.django_db


def test_workspace_creates_default_groups():
    workspace = Workspace.objects.create(name="Test Workspace")
    assert workspace.groups.get(name="Admin")
    assert workspace.groups.get(name="Member")


def test_workspace_creates_default_permissions():
    workspace = Workspace.objects.create(name="Test Workspace")
    assert workspace.groups.get(name="Admin").permissions.get(
        codename="manage_workspace"
    )
    assert len(workspace.groups.get(name="Member").permissions.all()) == 0

def test_workspace_add_admin_user():
    workspace = Workspace.objects.create(name="Test Workspace")
    user = User.objects.create_user(email="test@turntable.so")
    workspace.add_admin(user)

    admin_users = workspace.groups.get(name="Admin").users.all()
    assert user in admin_users


def remoke_admin_to_member():
    workspace = Workspace.objects.create(name="Test Workspace")
    user = User.objects.create_user(email="test@turntable.so")
    workspace.add_admin(user)

    admin_users = workspace.groups.get(name="Admin").users.all()
    assert user in admin_users

    workspace.add_member(user)
    member_users = workspace.groups.get(name="Member").users.all()
    admin_users = workspace.groups.get(name="Admin").users.all()

    assert user in member_users
    assert user not in admin_users


def test_user_permissions():
    workspace = Workspace.objects.create(name="Test Workspace")
    user = User.objects.create_user(email="test@turntable.so")
    workspace.add_admin(user)
    assert user.workspace_groups.get(workspace=workspace).permissions.get(
        codename="manage_workspace"
    )

    workspace.add_member(user)
    assert len(user.workspace_groups.get(workspace=workspace).permissions.all()) == 0
