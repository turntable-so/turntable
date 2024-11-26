import json

from channels.generic.websocket import WebsocketConsumer
from litellm import completion


class AIChatConsumer(WebsocketConsumer):
    def connect(self):
        print("AI Chat WebSocket Connected")
        self.accept()
        print("Connected")

    def disconnect(self, close_code):
        print(f"AI Chat WebSocket Disconnected with code: {close_code}")

    def receive(self, text_data):
        from app.core.inference.chat import (
            ChatRequestBody,
            build_context,
            recreate_lineage_object,
        )
        from app.core.inference.prompts import SYSTEM_PROMPT

        try:
            print(f"Received message: {text_data[:100]}...")
            user = self.scope["user"]
            data = ChatRequestBody.model_validate_json(text_data)
            lineage = recreate_lineage_object(data)

            prompt = build_context(
                user=user,
                message_history=data.message_history,
                lineage=lineage,
            )

            response = completion(
                temperature=0,
                model="claude-3-5-sonnet-20241022",
                messages=[
                    {"content": SYSTEM_PROMPT, "role": "system"},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )
            for chunk in response:
                print(chunk.choices[0].delta.content)
                self.send(
                    text_data=json.dumps(
                        {
                            "type": "message_chunk",
                            "content": chunk.choices[0].delta.content or "",
                        }
                    )
                )

            self.send(text_data=json.dumps({"type": "message_end"}))
        except Exception as e:
            print("Sending error message")
            self.send(text_data=json.dumps({"type": "error", "message": str(e)}))
