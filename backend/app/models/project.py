import os
import tempfile
import uuid
from contextlib import contextmanager

from django.conf import settings
from django.db import models
from git import Repo as GitRepo
from git.exc import GitCommandError

from app.models.repository import Repository
from app.models.workspace import Workspace


class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    branch_name = models.CharField(max_length=255, null=False)
    read_only = models.BooleanField(default=False)
    schema = models.CharField(max_length=255, null=False)
    source_branch = models.CharField(max_length=255, null=True)

    # relationships
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="projects"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    @property
    def is_main(self):
        return self.branch_name == self.repository.main_branch_name

    @property
    def is_cloned(self):
        with self._code_repo_path() as path:
            return os.path.exists(path)

    @property
    def pull_request_url(self):
        if not self.repository.git_repo_url:
            return None
        # Parse git URL into GitHub format
        url = self.repository.git_repo_url
        if url.startswith("git@"):
            # Convert SSH format to HTTPS
            url = url.replace(":", "/").replace("git@", "https://")

        if url.endswith(".git"):
            url = url[:-4]
        return f"{url}/compare/{self.source_branch}...{self.branch_name}"

    def clone(self, isolate: bool = False):
        with self._code_repo_path(isolate) as path:
            if os.path.exists(path) and ".git" in os.listdir(path):
                raise Exception("Repository already cloned")

            with self.repository.with_ssh_env() as env:
                repo = GitRepo.clone_from(self.repository.git_repo_url, path, env=env)

                # Fetch the latest changes from the remote
                repo.remotes.origin.fetch(env=env)

                # switch to the branch
                self.checkout(repo_override=repo, env_override=env)

        return True

    def checkout(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> str:
        with self.repository.with_ssh_env(env_override) as env:
            with self._code_repo_path(isolate) as path:
                repo = repo_override or GitRepo(path)
                # Fetch the latest changes from the remote
                repo.remotes.origin.fetch(env=env)
                repo.git.checkout(self.branch_name, env=env)
                return self.branch_name

    def commit(
        self,
        commit_message: str,
        file_paths: list[str],
        user_email: str,
    ):
        with self._code_repo_path() as repo_path:
            with self.repository.with_ssh_env() as env:
                repo = GitRepo(repo_path)

                with repo.config_writer() as git_config:
                    # Configure the user name and email
                    # github doesn't actually use this, but it's required by git
                    git_config.set_value("user", "name", "NAME")
                    # github uses the email for commit authorship
                    git_config.set_value("user", "email", user_email)

                    # Add each specified file
                    for file_path in file_paths:
                        repo.git.add(os.path.join(repo.working_tree_dir, file_path))

                    # Commit the changes
                    repo.git.commit(m=commit_message, env=env)

                    # Push to remote
                    repo.git.push("origin", self.branch_name, env=env)

                    # Revert the configs
                    git_config.set_value("user", "name", "")
                    git_config.set_value("user", "email", "")
        return True

    def discard_changes(self):
        with self.repo_context() as (repo, env):
            # Reset all staged changes
            repo.index.reset()

            # Discard all unstaged changes
            repo.git.checkout("--", ".")

            # Clean untracked files and directories
            repo.git.clean("-fd")

        return True

    @contextmanager
    def _code_repo_path(
        self, isolate: bool = False, separation_id: uuid.UUID | None = None
    ):
        path = os.path.join(
            "ws",
            str(self.workspace_id),
            str(self.repository_id),
            str(self.id),
            str(separation_id) if separation_id is not None else str(self.id),
            self.repository.repo_name,
        )
        if os.getenv("FORCE_NO_ISOLATE") == "true":
            yield os.path.join(settings.MEDIA_ROOT, path)
        elif isolate or os.getenv("FORCE_ISOLATE") == "true":
            with tempfile.TemporaryDirectory() as temp_dir:
                yield os.path.join(temp_dir, path)
        else:
            yield os.path.join(settings.MEDIA_ROOT, path)

    @contextmanager
    def repo_context(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> tuple[GitRepo, dict[str, str] | None]:
        if repo_override is not None and env_override is not None:
            yield repo_override, env_override
            return

        elif repo_override is not None:
            with self.repository.with_ssh_env(env_override) as env:
                yield repo_override, env
                return

        with self._code_repo_path(isolate) as path:
            if os.path.exists(path) and ".git" in os.listdir(path):
                with self.repository.with_ssh_env(env_override) as env:
                    repo = GitRepo(path)
                    yield repo, env
                    return

            with self.repository.with_ssh_env(env_override) as env:
                repo = GitRepo.clone_from(self.repository.git_repo_url, path, env=env)

                # Fetch the latest changes from the remote
                repo.remotes.origin.fetch(env=env)

                # switch to the branch
                self.checkout(isolate=isolate, repo_override=repo, env_override=env)

                yield repo, env
                return

    def create_git_branch(
        self,
        source_branch: str,
    ) -> str:
        with self.repository.with_ssh_env() as env:
            with tempfile.TemporaryDirectory() as tmp_dir:
                repo = GitRepo.init(tmp_dir)

                repo.git.fetch(
                    self.repository.git_repo_url,
                    f"{source_branch}:refs/remotes/origin/{source_branch}",
                    env=env,
                )

                # Create and checkout new branch
                repo.create_head(
                    self.branch_name, f"refs/remotes/origin/{source_branch}"
                )
                repo.git.push(
                    self.repository.git_repo_url, f"{self.branch_name}", env=env
                )

            return self.branch_name

    def git_pull(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> str:
        with self.repo_context(isolate, repo_override, env_override) as (
            repo,
            env,
        ):
            if repo.is_dirty(untracked_files=True):
                raise GitCommandError(
                    "DIRTY_WORKING_DIRECTORY",
                    "The working directory has uncommitted changes.",
                )

            # Fetch the latest changes
            repo.remotes.origin.fetch(env=env)

            # Get the current branch
            current_branch = repo.active_branch

            # Pull the latest changes
            repo.git.pull("origin", current_branch.name, env=env)

            return True
