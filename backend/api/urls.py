"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers

from app.views import (
    AssetViewSet,
    BlockViewSet,
    ExecuteQueryView,
    GithubInstallationViewSet,
    InvitationViewSet,
    LineageViewSet,
    NotebookViewSet,
    ResourceViewSet,
    SSHViewSet,
    WorkflowViews,
    WorkspaceGroupViewSet,
    WorkspaceViewSet,
    healthcheck,
)

from .views import CustomUserViewSet, LogoutView, OAuthView

router = routers.DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspace")
router.register(r"resources", ResourceViewSet, basename="resource")
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"lineage", LineageViewSet, basename="lineage")
router.register(r"workspace_groups", WorkspaceGroupViewSet, basename="workspace_group")
router.register(r"invitations", InvitationViewSet, basename="invitation")
router.register(r"users/invitations", CustomUserViewSet, basename="user")
router.register(r"github", GithubInstallationViewSet, basename="github")
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"blocks", BlockViewSet, basename="block")

urlpatterns = [
    path("oauth/auth", OAuthView.as_view(), name="oauth-auth"),
    path("healthcheck/", healthcheck, name="healthcheck"),
    path(
        "notebooks/<str:notebook_id>/blocks/<str:block_id>/query/",
        ExecuteQueryView.as_view(),
        name="execute_query",
    ),
    path(
        "workflows/<str:workflow_run_id>/",
        WorkflowViews.as_view(),
        name="get_workflow_status",
    ),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/logout", LogoutView.as_view()),
    path("admin/", admin.site.urls),
    path(
        "invitations/",
        include(("invitations.urls", "invitations"), namespace="invitations"),
    ),
    path("ssh/", SSHViewSet.as_view()),
    re_path(
        r"^lineage/(?P<pk>.+)/$",
        LineageViewSet.as_view({"get": "retrieve"}),
        name="lineage-detail",
    ),
    re_path(
        r"^assets/(?P<pk>.+)/$",
        AssetViewSet.as_view({"get": "retrieve"}),
        name="asset-detail",
    ),
    path("", include(router.urls)),
]
