import json
import logging
import asyncio
from app.core.inference.chat import EDIT_PROMPT_SYSTEM, SYSTEM_PROMPT, build_context
from channels.generic.websocket import AsyncWebsocketConsumer
from litellm import completion
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class TestStreamingConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        self.group_name = f"workspace_{self.workspace_id}"
        logger.info(f"Connecting to WebSocket for workspace: {self.workspace_id}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        logger.info(
            f"Disconnected from WebSocket for workspace: {self.workspace_id} with close code: {close_code}"
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def workflow_status_update(self, event):
        logger.info(
            f"Sending status update for workflow: {event['workflow_run_id']} with status: {event['status']}"
        )
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "workflow_run_id": event["workflow_run_id"],
                    "resource_id": event["resource_id"],
                }
            )
        )


class WorkflowRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        self.group_name = f"workspace_{self.workspace_id}"
        logger.info(f"Connecting to WebSocket for workspace: {self.workspace_id}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        logger.info(
            f"Disconnected from WebSocket for workspace: {self.workspace_id} with close code: {close_code}"
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def workflow_status_update(self, event):
        logger.info(
            f"Sending status update for workflow: {event['workflow_run_id']} with status: {event['status']}"
        )
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "workflow_run_id": event["workflow_run_id"],
                    "resource_id": event["resource_id"],
                }
            )
        )


# SYSTEM_PROMPT = """
# You are an expert data analyst who is proficient at writing and modifying POSTGRES sql and dbt (data build tool) models.

# Rules:
# - You are tasked with modifying a dbt (data build tool) model includes editing sql, jinja templating or adding additional sql.
# - You write syntactically correct sql that uses best practices such as using CTEs, qualifying columns and good variable name choices.
# - You will ONLY respond with the changed code for the entire file. NEVER offer an explanation or other artifacts besides the entire dbt model file
# - You will be provided with the schema for the dbt model as well as its data lineage and associated model schemas to help you write the sql transform that is correct and accurate
# - Use {{ ref('<model_name>')}} when referencing tables in queries
# - IMPORTANT: do not modify sql styling or formatting in any way
# - Respond in markdown format and just reply with the sql in a code block
# """


class ChatInferenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket Connected")

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")
        pass

    async def receive(self, text_data):
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
