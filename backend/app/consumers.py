import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)
from litellm import completion


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

CHAT_PROMPT_NO_CONTEXT = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.

Rules:
- Be as helpful as possible and answer all questions to the best of your ability.
- Please reference the latest dbt documentation at docs.getdbt.com if needed
- You will only respond in markdown, using headers, paragraph, bulleted lists and sql/dbt code blocks if needed for the best answer quality possible
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
"""


# def infer(user_prompt: str):
#     response = completion(
#         temperature=0.0,
#         model="gpt-4o",
#         messages=[
#             {"content": SYSTEM_PROMPT, "role": "system"},
#             {"role": "user", "content": user_prompt},
#         ],
#         stream=True,
#     )
#     for chunk in response:
#         yield (chunk.choices[0].delta.content or "")


def infer(user_prompt: str):
    return completion(
        temperature=0.5,
        model="gpt-4o",
        messages=[
            {"content": CHAT_PROMPT_NO_CONTEXT, "role": "system"},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )


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
        async for chunk in response:
            content = chunk.choices[0].delta.content or ""
            print(content, flush=True)
            await self.send(
                text_data=json.dumps({"type": "message_chunk", "content": content})
            )

        self.send(text_data=json.dumps({"type": "message_end"}))


class TestStreamingInference(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket Connected")

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        print(f"Received message: {message}")

        for i in range(10):
            await asyncio.sleep(0.5)
            print(f"Sending message: {i+1}")
            await self.send(
                text_data=json.dumps(
                    {"type": "message_chunk", "content": f"Echo {i+1}: {message}"}
                )
            )

        await self.send(text_data=json.dumps({"type": "message_end"}))
