import asyncio

import pytest
from channels.testing import WebsocketCommunicator

from api.asgi import application
from app.consumers.dbt_command_consumer import (
    DBT_COMMAND_STREAM_TIMEOUT,
)


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_postgres", "transactional_db")
class TestDBTCommandConsumer:
    url = "/ws/dbt_command/"

    async def test_no_token(self):
        communicator = WebsocketCommunicator(application, self.url)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

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
                response = await communicator.receive_from(
                    timeout=DBT_COMMAND_STREAM_TIMEOUT
                )
                out += response
        except (asyncio.TimeoutError, AssertionError):
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
            await communicator.receive_from(timeout=1)
        except (asyncio.TimeoutError, AssertionError):
            pass

        await communicator.send_json_to({"action": "cancel"})

        out = ""
        try:
            while True:
                response = await communicator.receive_from(timeout=10)
                out += response
        except (asyncio.TimeoutError, AssertionError):
            pass

        assert "WORKFLOW_CANCELLED" in out
        await communicator.disconnect()
