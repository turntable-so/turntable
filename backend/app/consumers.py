import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)
from litellm import completion


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


SYSTEM_PROMPT = """
You are an expert data analyst who is proficient at writing and modifying POSTGRES sql and dbt (data build tool) models.

Rules:
- You are tasked with modifying a dbt (data build tool) model includes editing sql, jinja templating or adding additional sql.
- You write syntactically correct sql that uses best practices such as using CTEs, qualifying columns and good variable name choices.
- You will ONLY respond with the changed code for the entire file. NEVER offer an explanation or other artifacts besides the entire dbt model file
- You will be provided with the schema for the dbt model as well as its data lineage and associated model schemas to help you write the sql transform that is correct and accurate
- Use {{ ref('<model_name>')}} when referencing tables in queries
- IMPORTANT: do not modify sql styling or formatting in any way
- Respond in markdown format and just reply with the sql in a code block
"""


def infer(user_prompt: str):
    response = completion(
        temperature=0.0,
        model="gpt-4o",
        messages=[
            {"content": SYSTEM_PROMPT, "role": "system"},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
    for chunk in response:
        yield (chunk.choices[0].delta.content or "")


class StreamingInferenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        print("WebSocket Connected")

    async def disconnect(self, close_code):
        # Called when the socket closes
        print("WebSocket Disconnected")

    async def receive(self, text_data):
        # Receive message from WebSocket
        data = json.loads(text_data)
        message = data.get("message", "")
        print(f"Received message: {message}")

        response = infer(message)
        for chunk in response:
            await self.send(text_data=json.dumps({"type": "message_chunk", "content": chunk}))

        await self.send(text_data=json.dumps({"message_end": True}))
