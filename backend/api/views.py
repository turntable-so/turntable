from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as regular_requests
from djoser.views import UserViewSet
from rest_framework.decorators import action
from invitations.utils import get_invitation_model
Invitation = get_invitation_model()
from app.models import (
        User,
    )

class LogoutView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        invitation_code = request.data.get('invitationCode', '')
        if invitation_code:
            try:
                invitation = Invitation.objects.get(key=invitation_code)

                if invitation.accepted:
                    return Response({"error": "Invitation code has already been accepted"}, status=status.HTTP_400_BAD_REQUEST)
                if invitation.email != request.data.get('email'):
                    return Response({"error": "Invitation email does not match"}, status=status.HTTP_400_BAD_REQUEST)
            except Invitation.DoesNotExist:
                return Response({"error": "Invitation code does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED and invitation_code:
            # Mark the invitation as accepted if needed
            invitation.accepted = True
            original_user = invitation.inviter
            workspace = original_user.current_workspace()
            workspace.add_member(response.data['id'])
            invitation.save()
        return response
    
class OAuthView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        token = request.data.get('token')
        provider = request.data.get('provider')
        invitation_code = request.data.get('invitation_code')
        if not token or not provider:
            return Response({'detail': 'Token and provider are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if provider == 'google':
            try:
                id_info = id_token.verify_oauth2_token(token, requests.Request())
                if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')

                email = id_info['email']
                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.set_unusable_password()
                    user.save()
                    if invitation_code:
                        try:
                            invitation = Invitation.objects.get(key=invitation_code)
                            if invitation.email == email:
                                invitation.accepted = True
                                original_user = invitation.inviter
                                workspace = original_user.current_workspace()
                                workspace.add_member(user.id)
                                invitation.save()
                        except Exception as e:
                            print(e)

                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            except ValueError:
                return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        if provider == 'github':
            try:
                headers = {'Authorization': f'token {token}'}
                response = regular_requests.get('https://api.github.com/user/emails', headers=headers)
                
                if response.status_code != 200:
                    return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
                
                emails = response.json()
                
                # Extract the primary email
                primary_email = None
                for email in emails:
                    if email['primary']:
                        primary_email = email['email']
                        break
                print("Primary email: ", primary_email)
                if not primary_email:
                    return Response({'detail': 'Primary email not found.'}, status=status.HTTP_400_BAD_REQUEST)

                # Get or create the user
                email = primary_email
                user, created = User.objects.get_or_create(email=email)

                if created:
                    user.set_unusable_password()
                    user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            
            except requests.RequestException as e:
                return Response({'detail': 'Error verifying token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Provider not supported.'}, status=status.HTTP_400_BAD_REQUEST)