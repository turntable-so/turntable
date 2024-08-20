import os

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from app.models import User, Workspace
from app.models.git_connections import SSHKey
from app.services.code_repo_service import CodeRepoService

User = get_user_model()


@pytest.mark.django_db
class CodeRepoServiceTests(TestCase):

    def setUp(self):
        # Set up initial data
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.workspace = Workspace.objects.create(name="Test workspace")
        self.workspace.users.add(self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_repo_connection(self):
        ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDsLPNCaBeZQynaRQBR6wDCWbWYYSsj3oNOSTNvveQn9z0AO3b4dTQ25Fzo3UBm5cKkvk/Mim1uEbCX4hjPR7VSM+cgLEYWTnlb/SGKSsbgmEDMlO5Zt6zV4EswBUCkLf4ZRzKZdpxHOehGqhZC/7LcuO+wdCtG9zP1lWVe+2Dw8GiOLL6datCL4n01/xwpnxQaYtvr8pyud/FJIGh/jU7/8uaGb/RwvwbT5/XhA+H3eu3FS4dQK4g95nhtg5ApTW0NZWp4reLn/yu0DfFhCwLKyvcrot0A5HEhQNZFJqou691BmJ47GgSHg+EFOE+WNeitbhqJgs0usZ02Au00rl7B"
        private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA7CzzQmgXmUMp2kUAUesAwlm1mGErI96DTkkzb73kJ/c9ADt2\n+HU0NuRc6N1AZuXCpL5PzIptbhGwl+IYz0e1UjPnICxGFk55W/0hikrG4JhAzJTu\nWbes1eBLMAVApC3+GUcymXacRznoRqoWQv+y3LjvsHQrRvcz9ZVlXvtg8PBojiy+\nnWrQi+J9Nf8cKZ8UGmLb6/KcrnfxSSBof41O//Lmhm/0cL8G0+f14QPh93rtxUuH\nUCuIPeZ4bYOQKU1tDWVqeK3i5/8rtA3xYQsCysr3K6LdAORxIUDWRSaqLuvdQZie\nOxoEh4PhBThPljXorW4aiYLNLrGdNgLtNK5ewQIDAQABAoIBADoOsLwF16tC4fJ4\nnOQGV5jvMZ9kX5UBOZkQkJbrAL+8XOAGPjBEq5HE4HwUC6Vf3NHfwMEg1FbG/XjQ\nyVWHJLEw9iOoDpCkONwepVSYHjyO4PsJr3AZoWCwMvt6hxH1Bm5TXMJx8Gfn+cwJ\nOtC8h80Pn0hqvkrDMSAxWgqX1BRWJAVEHB1AHqWydWf5XOxJsYw48xXY/iX928Yy\nNwPFWfayyxzqSf+Sv0qjxthqScpvKBHb/J9RXjlD3149y2Fl9pKdeThyKnVGLQe3\nIApIU0QGokDXVo05EUSWFRRDp2A2aqhxuTuqYIwkwZEZbgrk6IAxzgBPVY4cGQsl\nRpaMEoMCgYEA/OBQ9IvxterQa7rZLY5s/usg3xWccavsyYCcwo3eCsuOiFGfKxD3\nYEwGsnxYgpoSxf6R2NtlvQxms4hWBIgzErruTPuRBWHCzvCOKeT+8fU5G1uholmJ\nB0CW43utDnEe+99jcaE5tJyfFdG8wnqrtmx5OZLwm3Y9RF67PMOahWMCgYEA7xfS\nFxk3QaSGaDwnqGSKC79DZaD3ybLAIyJt8FOcSCL+/8RmyLmOUhNrTVp3O7o5Akhv\nxKp3SYjgyvzBqBXwRJdJBzIrDIVP4PLRXySEjYkRVXPtYD29l3jlGOTwCUZri/Ot\nTT/XG7vOWnZHAf/FuxdPsD/wYshXoYLbo8Ob5osCgYEA4P2cSdjxuFAyHIfkj3n3\nVGBToOkThrfXN/msgBXFh4lRScyFd8Xis9Uw6EFmZt068trrXSznump8PiSBlAqy\nlmmneOsjPsyajZDOjEvo4dKzernueAp9tuwq1D/H29+eF6/MRN+T/jST/s/byJVo\njii5OxaX6VosbNZ0dT38D80CgYBufWWbQw3kCfILDXGOQhgBYbv1pTOdRDvCgNCp\ndRoNxA5viAWv0QBSMaMuthXPxjk+Mtdj3RsPInAvniqoUKseJ4OaDbcTLDBD1jKn\ncyrGdYdLJC2Ygi+xZi8JGBNNVfuxS0TVJCF2MY4lA+/AnsBzu0waORIPtGG6w8xY\nm7baDQKBgQCniuzZn/jsm4jc+LN6vPPIwjrg0piAXiPtcEcUfj6pemshJLLuP3tq\n0SEplqWto0/Db0DFK2o480XMfx9EWh83CG5Lts8o8lX2wv7yAHrZh1eAtPdHuArR\nLqSiF05NRy5rqRPYvTyCQp/5otIOlTUuKQRD6N6i9PMFR5M9skiiUQ==\n-----END RSA PRIVATE KEY-----\n"
        git_repo_url = "git@github.com:turntable-so/turntable_dbt.git"

        SSHKey.objects.create(
            workspace_id=self.workspace.id,
            public_key=ssh_key,
            private_key=private_key,
        )

        data = {
            "public_key": ssh_key,
            "git_repo_url": git_repo_url,
        }

        coderepo_service = CodeRepoService(workspace_id=self.workspace.id)
        res = coderepo_service.test_repo_connection(
            public_key=data.get("public_key"),
            git_repo_url=data.get("git_repo_url"),
        )
        assert res["success"] == True

    def test_repo_pull(self):
        ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDsLPNCaBeZQynaRQBR6wDCWbWYYSsj3oNOSTNvveQn9z0AO3b4dTQ25Fzo3UBm5cKkvk/Mim1uEbCX4hjPR7VSM+cgLEYWTnlb/SGKSsbgmEDMlO5Zt6zV4EswBUCkLf4ZRzKZdpxHOehGqhZC/7LcuO+wdCtG9zP1lWVe+2Dw8GiOLL6datCL4n01/xwpnxQaYtvr8pyud/FJIGh/jU7/8uaGb/RwvwbT5/XhA+H3eu3FS4dQK4g95nhtg5ApTW0NZWp4reLn/yu0DfFhCwLKyvcrot0A5HEhQNZFJqou691BmJ47GgSHg+EFOE+WNeitbhqJgs0usZ02Au00rl7B"
        private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA7CzzQmgXmUMp2kUAUesAwlm1mGErI96DTkkzb73kJ/c9ADt2\n+HU0NuRc6N1AZuXCpL5PzIptbhGwl+IYz0e1UjPnICxGFk55W/0hikrG4JhAzJTu\nWbes1eBLMAVApC3+GUcymXacRznoRqoWQv+y3LjvsHQrRvcz9ZVlXvtg8PBojiy+\nnWrQi+J9Nf8cKZ8UGmLb6/KcrnfxSSBof41O//Lmhm/0cL8G0+f14QPh93rtxUuH\nUCuIPeZ4bYOQKU1tDWVqeK3i5/8rtA3xYQsCysr3K6LdAORxIUDWRSaqLuvdQZie\nOxoEh4PhBThPljXorW4aiYLNLrGdNgLtNK5ewQIDAQABAoIBADoOsLwF16tC4fJ4\nnOQGV5jvMZ9kX5UBOZkQkJbrAL+8XOAGPjBEq5HE4HwUC6Vf3NHfwMEg1FbG/XjQ\nyVWHJLEw9iOoDpCkONwepVSYHjyO4PsJr3AZoWCwMvt6hxH1Bm5TXMJx8Gfn+cwJ\nOtC8h80Pn0hqvkrDMSAxWgqX1BRWJAVEHB1AHqWydWf5XOxJsYw48xXY/iX928Yy\nNwPFWfayyxzqSf+Sv0qjxthqScpvKBHb/J9RXjlD3149y2Fl9pKdeThyKnVGLQe3\nIApIU0QGokDXVo05EUSWFRRDp2A2aqhxuTuqYIwkwZEZbgrk6IAxzgBPVY4cGQsl\nRpaMEoMCgYEA/OBQ9IvxterQa7rZLY5s/usg3xWccavsyYCcwo3eCsuOiFGfKxD3\nYEwGsnxYgpoSxf6R2NtlvQxms4hWBIgzErruTPuRBWHCzvCOKeT+8fU5G1uholmJ\nB0CW43utDnEe+99jcaE5tJyfFdG8wnqrtmx5OZLwm3Y9RF67PMOahWMCgYEA7xfS\nFxk3QaSGaDwnqGSKC79DZaD3ybLAIyJt8FOcSCL+/8RmyLmOUhNrTVp3O7o5Akhv\nxKp3SYjgyvzBqBXwRJdJBzIrDIVP4PLRXySEjYkRVXPtYD29l3jlGOTwCUZri/Ot\nTT/XG7vOWnZHAf/FuxdPsD/wYshXoYLbo8Ob5osCgYEA4P2cSdjxuFAyHIfkj3n3\nVGBToOkThrfXN/msgBXFh4lRScyFd8Xis9Uw6EFmZt068trrXSznump8PiSBlAqy\nlmmneOsjPsyajZDOjEvo4dKzernueAp9tuwq1D/H29+eF6/MRN+T/jST/s/byJVo\njii5OxaX6VosbNZ0dT38D80CgYBufWWbQw3kCfILDXGOQhgBYbv1pTOdRDvCgNCp\ndRoNxA5viAWv0QBSMaMuthXPxjk+Mtdj3RsPInAvniqoUKseJ4OaDbcTLDBD1jKn\ncyrGdYdLJC2Ygi+xZi8JGBNNVfuxS0TVJCF2MY4lA+/AnsBzu0waORIPtGG6w8xY\nm7baDQKBgQCniuzZn/jsm4jc+LN6vPPIwjrg0piAXiPtcEcUfj6pemshJLLuP3tq\n0SEplqWto0/Db0DFK2o480XMfx9EWh83CG5Lts8o8lX2wv7yAHrZh1eAtPdHuArR\nLqSiF05NRy5rqRPYvTyCQp/5otIOlTUuKQRD6N6i9PMFR5M9skiiUQ==\n-----END RSA PRIVATE KEY-----\n"
        git_repo_url = "git@github.com:turntable-so/turntable_dbt.git"

        SSHKey.objects.create(
            workspace_id=self.workspace.id,
            public_key=ssh_key,
            private_key=private_key,
        )
        data = {
            "public_key": ssh_key,
            "git_repo_url": git_repo_url,
        }
        coderepo_service = CodeRepoService(workspace_id=self.workspace.id)
        with coderepo_service.repo_context(
            public_key=data.get("public_key"),
            git_repo_url=data.get("git_repo_url"),
        ) as repo:
            assert len(os.listdir(repo)) > 3
