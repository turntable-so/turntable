from datetime import time
import os
import asyncio
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
            EDIT_PROMPT_SYSTEM,
            SYSTEM_PROMPT,
            build_context,
            recreate_lineage_object,
        )

        print(f"Received message: {text_data[:100]}...")
        data = json.loads(text_data)
        user = self.scope["user"]
        lineage = recreate_lineage_object(data)
        if data.get("type") == "completion":
            prompt = build_context(
                user=user,
                instructions=data.get("instructions"),
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
            print(prompt)
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

        if data.get("type") == "single_file_edit":
            prompt = build_context(
                user=user,
                lineage=lineage,
                instructions=data.get("instructions"),
                current_file=data.get("current_file"),
            )

            response = completion(
                temperature=0,
                model="claude-3-5-sonnet-20241022",
                messages=[
                    {"content": EDIT_PROMPT_SYSTEM, "role": "system"},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )
            for chunk in response:
                self.send(
                    text_data=json.dumps(
                        {
                            "type": "single_file_edit_chunk",
                            "content": chunk.choices[0].delta.content or "",
                        }
                    )
                )

            self.send(text_data=json.dumps({"type": "single_file_edit_end"}))
