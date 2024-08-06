import os
import tempfile
import zipfile
from contextlib import contextmanager
from io import BytesIO

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from githubkit import AppInstallationAuthStrategy, GitHub
from githubkit.rest import Repository as GitHubRepository

from workflows.utils.encoding import decode_base64


class GithubService:
    workspace_id: str
    github_app_id: str
    github_private_key: str
    installation_id: str

    def __init__(self, workspace_id: str, installation_id: str):
        self.workspace_id = workspace_id
        self.installation_id = installation_id

        self.github_app_id = os.getenv("GITHUB_APP_ID")
        if self.github_app_id is None:
            raise ValueError("GITHUB_APP_ID is not set")

        self.github_private_key = decode_base64(os.getenv("GITHUB_PRIVATE_KEY_BASE64"))
        if self.github_private_key is None:
            raise ValueError("GITHUB_PRIVATE_KEY_BASE64 is not set")

    def get_client(self) -> GitHub:
        github = GitHub(
            AppInstallationAuthStrategy(
                app_id=self.github_app_id,
                private_key=self.github_private_key,
                installation_id=self.installation_id,
            )
        )
        return github

    def get_repositories(self) -> list[GitHubRepository]:
        client = self.get_client()
        return client.rest.apps.list_repos_accessible_to_installation(
            per_page=1000
        ).parsed_data.repositories

    def get_repository_by_id(self, repo_id: int) -> GitHubRepository:
        repositories = self.get_repositories()
        for repo in repositories:
            if repo.id == repo_id:
                return repo

        raise ValueError(f"Repository with id {repo_id} not found")

    def get_zipball(self, repo_id: int):
        client = self.get_client()
        repo: GitHubRepository = self.get_repository_by_id(repo_id)
        contents = client.rest.repos.download_zipball_archive(
            owner=repo.owner.login,
            repo=repo.name,
            ref=repo.default_branch,
        ).content
        return contents

    def generate_ssh_rsa(self):
        # Generate a new RSA key pair
        key = rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537, key_size=2048
        )

        # Serialize the public key
        public_key = key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )

        private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return public_key.decode("utf-8"), private_key.decode("utf-8")

    @contextmanager
    def repo_context(self, repo_id: str):
        zip_contents = self.get_zipball(repo_id)
        zip_file_like = BytesIO(zip_contents)
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extracting contents of the zip file
            with zipfile.ZipFile(zip_file_like, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            yield (zip_contents, temp_dir)
