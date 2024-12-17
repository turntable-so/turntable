import json

from channels.generic.websocket import WebsocketConsumer
from sentry_sdk import capture_exception


class InstantApplyConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        from ai.core.instant_apply import stream_instant_apply
        from ai.core.models import InstantApplyRequestBody

        try:
            user = self.scope["user"]
            payload = InstantApplyRequestBody.model_validate_json(text_data)
            stream = stream_instant_apply(
                payload=payload,
                user_id=user.id,
            )
            for chunk in stream:
                self.send(
                    text_data=json.dumps({"type": "message_chunk", "content": chunk})
                )

            self.send(text_data=json.dumps({"type": "message_end"}))
        except Exception as e:
            print(e)
            capture_exception(e)
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Something went wrong"}
                )
            )
