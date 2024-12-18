import json
import time

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ai.core.chat import stream_chat_completion
from ai.core.models import ChatRequestBody


class EvalViewSet(viewsets.ViewSet):
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow anyone to access this view

    @action(detail=False, methods=["post"])
    def eval(self, request):
        request_data = json.loads(request.body.decode("utf-8"))

        payload = ChatRequestBody.model_validate_json(
            json.dumps(request_data["payload"])
        )
        api_keys = request_data["api_keys"]
        workspace_instructions = request_data["workspace_instructions"]
        dialect = request_data["dialect"]

        start_time = time.time()
        first_token_time = None

        stream = stream_chat_completion(
            payload=payload,
            dbt_details=None,
            dialect=dialect,
            api_keys=api_keys,
            workspace_instructions=workspace_instructions,
        )
        result = ""
        for chunk in stream:
            if not first_token_time and chunk:
                first_token_time = time.time()
            result += chunk

        end_time = time.time()
        execution_time = round(end_time - start_time, 1)
        time_to_first_token = (
            round(first_token_time - start_time, 1) if first_token_time else None
        )

        return Response(
            {
                "result": result,
                "metadata": {
                    "execution_time": f"{execution_time}s",
                    "time_to_first_token": f"{time_to_first_token}s"
                    if time_to_first_token is not None
                    else None,
                },
            }
        )
