import json

from channels.generic.websocket import WebsocketConsumer
from litellm import completion
from sentry_sdk import capture_exception


class AIChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        print(f"AI Chat WebSocket Disconnected with code: {close_code}")

    def receive(self, text_data):
        from ai.core.chat import (
            ChatRequestBody,
            build_context,
            recreate_lineage_object,
        )
        from ai.core.prompts import SYSTEM_PROMPT

        try:
            user = self.scope["user"]
            workspace = user.current_workspace()
            dbt_details = workspace.get_dbt_dev_details()

            data = ChatRequestBody.model_validate_json(text_data)
            print("Data here: ", data)
            should_recreate_lineage = (
                data.asset_id is not None
                and data.related_assets is not None
                and data.asset_links is not None
                and data.column_links is not None
            )
            lineage = (
                recreate_lineage_object(
                    asset_id=data.asset_id,
                    related_assets=data.related_assets,
                    asset_links=data.asset_links,
                    column_links=data.column_links,
                )
                if should_recreate_lineage
                else None
            )
            print("\n\n\nbuilding prompt")
            prompt = build_context(
                lineage=lineage,
                message_history=data.message_history,
                dbt_details=dbt_details,
                context_files=data.context_files,
            )
            print("prompt built: ", prompt)

            message_history = []
            for idx, msg in enumerate(data.message_history):
                if idx == len(data.message_history) - 1:
                    msg.content = prompt
                message_history.append(msg.model_dump())

            messages = [
                {"content": SYSTEM_PROMPT, "role": "system"},
                *message_history,
            ]
            response = completion(
                temperature=0,
                model=data.model,
                messages=messages,
                stream=True,
            )
            for chunk in response:
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
            capture_exception(e)
            self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Something went wrong"}
                )
            )
