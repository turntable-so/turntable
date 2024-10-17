from rest_framework.views import APIView
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid
import json


class EchoMessageView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        if not message:
            return Response({"error": "Message is required"}, status=400)

        # Generate a unique channel name
        channel_name = f"echo_{uuid.uuid4()}"

        # Get the channel layer
        channel_layer = get_channel_layer()

        # Send the message to the consumer
        async_to_sync(channel_layer.send)(
            channel_name, {"type": "receive", "text": json.dumps({"message": message})}
        )

        return Response(
            {"message": "Echo process started", "channel_name": channel_name}
        )
