import json

from channels.generic.websocket import WebsocketConsumer


class AIChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        print(f"AI Chat WebSocket Disconnected with code: {close_code}")

    def receive(self, text_data):
        from ai.core.chat import stream_chat_completion
        from ai.core.models import ChatRequestBody

        try:
            user = self.scope["user"]
            workspace = user.current_workspace()
            dbt_details = workspace.get_dbt_dev_details()
            data = ChatRequestBody.model_validate_json(text_data)
            stream = stream_chat_completion(payload=data, dbt_details=dbt_details, workspace=workspace)
            for chunk in stream:
                self.send(text_data=json.dumps({"type": "message_chunk", "content": chunk}))

            self.send(text_data=json.dumps({"type": "message_end"}))
        except Exception as e:
            print("An error occured: ", e)
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Something went wrong"}
                )
            )
