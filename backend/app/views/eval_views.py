import json

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
        request_data = json.loads(request.body.decode('utf-8'))
        
        payload = ChatRequestBody.model_validate_json(json.dumps(request_data["payload"]))
        api_keys = request_data["api_keys"]
        workspace_instructions = request_data["workspace_instructions"]
        dialect = request_data["dialect"]
        
        stream = stream_chat_completion(
            payload=payload,
            dbt_details=None,
            dialect=dialect,
            api_keys=api_keys,
            workspace_instructions=workspace_instructions,
        )
        result = "".join(stream)

        return Response({"result": result})
