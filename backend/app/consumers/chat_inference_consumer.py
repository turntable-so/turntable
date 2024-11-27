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
            workspace = user.current_workspace()
            dbt_details = workspace.get_dbt_dev_details()

            data = ChatRequestBody.model_validate_json(text_data)
            lineage = recreate_lineage_object(data)

            prompt = build_context(
                lineage=lineage,
                message_history=data.message_history,
                dbt_details=dbt_details,
                current_file=data.current_file,
            )

            response = completion(
                temperature=0,
                model=data.model,
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
