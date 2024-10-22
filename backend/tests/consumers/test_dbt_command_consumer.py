import pytest
from channels.testing import WebsocketCommunicator
from api.asgi import application
from rest_framework_simplejwt.exceptions import InvalidToken
import asyncio


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@pytest.mark.usefixtures("no_hatchet", "local_postgres")
class TestDBTCommandConsumer:
    url = "/ws/dbt_command/"

    async def test_no_token(self):
        communicator = WebsocketCommunicator(
            application,
            self.url
        )
        
        with pytest.raises(InvalidToken) as exc_info:
            await communicator.connect()
        
        assert "token_not_valid" in str(exc_info.value)
    
    async def test_valid_token(self, client_with_token):
        communicator = WebsocketCommunicator(
            application,
            f"{self.url}?token={client_with_token.access_token}"
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

        print("test_dbt_command_consumer - can send command")

        await communicator.send_json_to({
            "action": "start",
            "command": "ls"
        })

        print("test_dbt_command_consumer - sent command")

        try:
            while True:
                print("test_dbt_command_consumer - waiting for response")
                response = await communicator.receive_from()
                print("test_dbt_command_consumer - received response", response)
        except asyncio.TimeoutError:
            print("No more messages received.")

        raise Exception("test_dbt_command_consumer - test complete")
        await communicator.disconnect()
