import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from litellm import completion

from app.core.inference.chat import (
    EDIT_PROMPT_SYSTEM,
    SYSTEM_PROMPT,
    build_context,
    recreate_lineage_object,
)


class AIChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("AI Chat WebSocket Connected")
        await self.accept()
        print("Connected")

    async def disconnect(self, close_code):
        print(f"AI Chat WebSocket Disconnected with code: {close_code}")

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        data = json.loads(text_data)
        user = self.scope["user"]
        # print(data, flush=True)
        lineage = await sync_to_async(recreate_lineage_object)(data)
        if data.get("type") == "completion":
            prompt = await sync_to_async(build_context)(
                user=user,
                instructions=data.get("instructions"),
                lineage=lineage,
            )

            response = completion(
                temperature=0.1,
                model="gpt-4o",
                messages=[
                    {"content": SYSTEM_PROMPT, "role": "system"},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )
            for chunk in response:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "message_chunk",
                            "content": chunk.choices[0].delta.content or "",
                        }
                    )
                )
                await asyncio.sleep(0)

            await self.send(text_data=json.dumps({"type": "message_end"}))

        if data.get("type") == "single_file_edit":
            prompt = await sync_to_async(build_context)(
                user=user,
                lineage=lineage,
                instructions=data.get("instructions"),
                current_file=data.get("current_file"),
            )

            response = completion(
                temperature=0.1,
                model="gpt-4o",
                messages=[
                    {"content": EDIT_PROMPT_SYSTEM, "role": "system"},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )
            for chunk in response:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "single_file_edit_chunk",
                            "content": chunk.choices[0].delta.content or "",
                        }
                    )
                )
                await asyncio.sleep(0.01)

            await self.send(text_data=json.dumps({"type": "single_file_edit_end"}))
