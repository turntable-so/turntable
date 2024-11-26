import json
import time

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
            build_context,
            recreate_lineage_object,
        )
        from app.core.inference.prompts import SYSTEM_PROMPT

        self.send(text_data=json.dumps({"type": "message_chunk", "content": "Hi from the server"}))
        self.send(text_data=json.dumps({"type": "message_end"}))
        return

        try:
            print(f"Received message: {text_data[:100]}...")
            data = json.loads(text_data)
            user = self.scope["user"]
            lineage = recreate_lineage_object(data)

            print("Building context")
            start_time = time.time()
            prompt = build_context(
                user=user,
                instructions=data.get("instructions"),
                lineage=lineage,
            )
            end_time = time.time()
            print(f"Time taken to build context: {end_time - start_time} seconds")

            print(prompt)

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
