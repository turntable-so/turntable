from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import InvitationSerializer, WorkspaceSerializer
from app.models import Workspace
from invitations.utils import get_invitation_model
from app.utils.email import send_invite_email
from django.conf import settings

from dotenv import load_dotenv
load_dotenv()

Invitation = get_invitation_model()


class InvitationViewSet(viewsets.ModelViewSet):
    def create(self, request):
        email = request.data["email"]
        
        previous_invitation = Invitation.objects.filter(email=email)
        if (previous_invitation.exists()):
            return Response({"status": "success"})
        invitation = Invitation.create(email=email, inviter_id=request.user.id)
        url = settings.FE_URL
        send_invite_email(email, url + "signup?invitation_code=" + invitation.key)
        return Response({"status": "success"})
    
    def list(self, request):
        user = request.user
        invitations = Invitation.objects.filter(inviter_id=user.id)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        invitation = Invitation.objects.get(id=pk)
        serializer = InvitationSerializer(invitation)
        return Response(serializer.data)
        
