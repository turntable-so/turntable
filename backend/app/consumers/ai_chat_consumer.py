import asyncio
import json
import traceback
from app.core.inference.chat import (
    EDIT_PROMPT_SYSTEM,
    SYSTEM_PROMPT,
    build_context,
)
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from litellm import completion


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
        print(data, flush=True)
        if data.get("type") == "completion":
            related_assets = data.get("related_assets")
            if related_assets and len(related_assets) > 0:
                related_assets = ["0:" + id for id in related_assets]
            else:
                related_assets = []
            prompt = await sync_to_async(build_context)(
                related_assets=related_assets,
                instructions=data.get("instructions"),
                asset_links=data.get("asset_links"),
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
            related_assets = data.get("related_assets")
            if related_assets and len(related_assets) > 0:
                related_assets = ["0:" + id for id in related_assets]
            else:
                related_assets = []
            prompt = await sync_to_async(build_context)(
                related_assets=related_assets,
                instructions=data.get("instructions"),
                current_file=data.get("current_file"),
                asset_links=data.get("asset_links"),
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
