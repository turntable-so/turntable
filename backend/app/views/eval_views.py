import json
import time

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ai.core.chat import stream_chat_completion
from ai.core.instant_apply import stream_instant_apply
from ai.core.models import ChatRequestBody, InstantApplyRequestBody


class EvalViewSet(viewsets.ViewSet):
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow anyone to access this view

    @action(detail=False, methods=["post"])
    def eval(self, request):
        request_data = json.loads(request.body.decode("utf-8"))

        tags = request_data["tags"]
        payload = ChatRequestBody.model_validate_json(
            json.dumps(request_data["chat_payload"]["payload"])
        )
        api_keys = request_data["chat_payload"]["api_keys"]
        workspace_instructions = request_data["chat_payload"]["workspace_instructions"]
        dialect = request_data["chat_payload"]["dialect"]

        start_time = time.time()
        first_token_time = None

        stream = stream_chat_completion(
            payload=payload,
            dbt_details=None,
            dialect=dialect,
            api_keys=api_keys,
            workspace_instructions=workspace_instructions,
            tags=tags,
        )
        chat_result = ""
        for chunk in stream:
            if not first_token_time and chunk:
                first_token_time = time.time()
            chat_result += chunk

        end_time = time.time()
        execution_time = round(end_time - start_time, 1)
        time_to_first_token = (
            round(first_token_time - start_time, 1) if first_token_time else None
        )

        instant_apply_stream = stream_instant_apply(
            payload=InstantApplyRequestBody(
                base_file=request_data["instant_apply_payload"]["base_file"],
                change=chat_result,
            ),
            tags=tags,
        )
        instant_apply_result = ""
        for chunk in instant_apply_stream:
            instant_apply_result += chunk

        return Response(
            {
                "chat_result": chat_result,
                "instant_apply_result": instant_apply_result,
                "metadata": {
                    "execution_time": f"{execution_time}s",
                    "time_to_first_token": f"{time_to_first_token}s"
                    if time_to_first_token is not None
                    else None,
                },
            }
        )
