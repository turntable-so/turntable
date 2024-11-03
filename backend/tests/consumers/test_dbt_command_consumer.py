import asyncio

import pytest
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.exceptions import InvalidToken

from api.asgi import application


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@pytest.mark.usefixtures("custom_celery", "local_postgres")
class TestDBTCommandConsumer:
    url = "/ws/dbt_command/"

    async def test_no_token(self):
        communicator = WebsocketCommunicator(application, self.url)

        with pytest.raises(InvalidToken) as exc_info:
            await communicator.connect()

        assert "token_not_valid" in str(exc_info.value)

    async def test_valid_token(self, client_with_token):
        communicator = WebsocketCommunicator(
            application, f"{self.url}?token={client_with_token.access_token}"
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.usefixtures("enable_django_allow_async_unsafe")
    async def test_can_send_command(self, client_with_token):
        communicator = WebsocketCommunicator(
            application,
            f"{self.url}?token={client_with_token.access_token}",
        )
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({"action": "start", "command": "ls"})

        out = ""
        try:
            while True:
                response = await communicator.receive_from()
                out += response
        except asyncio.TimeoutError:
            pass

        assert "PROCESS_STREAM_SUCCESS" in out
        await communicator.disconnect()

    @pytest.mark.usefixtures("enable_django_allow_async_unsafe")
    async def test_can_cancel_command(self, client_with_token):
        communicator = WebsocketCommunicator(
            application,
            f"{self.url}?token={client_with_token.access_token}",
        )
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({"action": "start", "command": "ls"})

        # wait for the command to start
        try:
            await communicator.receive_from()
        except asyncio.TimeoutError:
            pass

        await communicator.send_json_to({"action": "cancel"})

        out = ""
        try:
            while True:
                response = await communicator.receive_from()
                out += response
        except asyncio.TimeoutError:
            pass

        assert "WORKFLOW_CANCELLED" in out
        await communicator.disconnect()
