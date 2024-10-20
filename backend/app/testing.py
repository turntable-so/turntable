if __name__ == "__main__":
    import django
    from django.conf import settings
    import asyncio
    import websockets
    import json

    django.setup()

    from app.models import User

    settings.ALLOWED_HOSTS = ["*"]
    user = User.objects.get(email="dev@turntable.so")
    workspace = user.current_workspace()

    async def connect_websocket():
        protocol = "ws"
        base = "localhost:8000"
        accessToken = "1234567890"
        uri = f"{protocol}://{base}/ws/dbt_command/{workspace.id}/?token={accessToken}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({"action": "start", "command": "ls"}))

            while True:
                try:
                    message = await websocket.recv()
                    print(message)
                    if message == "PROCESS_STREAM_SUCCESS":
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break

    asyncio.get_event_loop().run_until_complete(connect_websocket())
