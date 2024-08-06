import uuid

from django.db import models

from app.models.auth import User, Workspace


class SSHKey(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # fields
    public_key = models.TextField()
    private_key = models.TextField()

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]


class GithubInstallation(models.Model):
    # pk
    id = models.CharField(
        primary_key=True,
        max_length=255,
        default=uuid.uuid4,
    )

    # fields
    created_at = models.DateTimeField(auto_now_add=True)
    ssh_key = models.TextField(null=True)
    git_url = models.URLField(null=True)
    git_repo_type = models.CharField(max_length=255, null=True)
    main_git_branch = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super(GithubInstallation, self).save(*args, **kwargs)
