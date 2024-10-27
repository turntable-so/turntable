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
from app.views.embedding_views import EmbeddingViewSet
from app.views.settings_view import SettingsView
from app.views.inference_views import InferenceView
from app.views.project_views import ProjectViewSet
from app.views.query_views import DbtQueryPreviewView
from rest_framework import routers

from app.consumers import DBTCommandConsumer, WorkflowRunConsumer
from app.views import (
    AssetViewSet,
    BlockViewSet,
    ExecuteQueryView,
    HealthCheckViewSet,
    InvitationViewSet,
    LineageViewSet,
    NotebookViewSet,
    ResourceViewSet,
    SSHViewSet,
    SyncResourceView,
    TestResourceView,
    WorkflowViews,
    WorkspaceGroupViewSet,
    WorkspaceViewSet,
)
from app.views.project_views import ProjectViewSet
from app.views.query_views import DbtQueryPreviewView
from app.views.settings_view import SettingsView

from .views import CustomUserViewSet, LogoutView, OAuthView

router = routers.DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspace")
router.register(r"resources", ResourceViewSet, basename="resource")
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"lineage", LineageViewSet, basename="lineage")
router.register(r"workspace_groups", WorkspaceGroupViewSet, basename="workspace_group")
router.register(r"invitations", InvitationViewSet, basename="invitation")
router.register(r"users/invitations", CustomUserViewSet, basename="user")
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"blocks", BlockViewSet, basename="block")
router.register(r"healthcheck", HealthCheckViewSet, basename="healthcheck")
router.register(r"project", ProjectViewSet, basename="project")
router.register(r"embedding", EmbeddingViewSet, basename="embedding")

urlpatterns = [
    path("oauth/auth", OAuthView.as_view(), name="oauth-auth"),
    path(
        "notebooks/<str:notebook_id>/blocks/<str:block_id>/query/",
        ExecuteQueryView.as_view(),
        name="execute_query",
    ),
    path(
        "query/preview/",
        DbtQueryPreviewView.as_view(),
        name="dbt_query_preview",
    ),
    path(
        "resources/<str:resource_id>/sync/",
        SyncResourceView.as_view(),
        name="sync_resource",
    ),
    path(
        "resources/<str:resource_id>/test/",
        TestResourceView.as_view(),
        name="test_resource",
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
    path("assets/index/", AssetViewSet.as_view({"get": "index"})),
    re_path(
        r"^assets/(?P<pk>.+)/$",
        AssetViewSet.as_view({"get": "retrieve"}),
        name="asset-detail",
    ),
    path("ws/subscribe/<str:workspace_id>/", WorkflowRunConsumer.as_asgi()),
    path("ws/dbt_command/<str:workspace_id>/", DBTCommandConsumer.as_asgi()),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("infer/", InferenceView.as_view(), name="inference"),
    path("", include(router.urls)),
]
