
from django.test import TestCase
from rest_framework.test import APIClient
from app.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import Workspace
from invitations.utils import get_invitation_model
import json

Invitation = get_invitation_model()
class CustomUserViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password')
        self.invitation = Invitation.objects.create(email='test2user@example.com', key='invitekey', inviter=self.user)
        self.workspace = Workspace.objects.create(name='Workspace')
        self.workspace.users.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_user_with_invitation(self):
        data = {
            'password': 'NEwpassword123!',
            'email': 'test2user@example.com',
            'invitationCode': self.invitation.key
        }
        response = self.client.post('/users/invitations/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_user_invalid_invitation(self):
        data = {
            'password': 'NEwpassword123!',
            'email': 'wrongemail@example.com',
            'invitationCode': self.invitation.key
        }
        response = self.client.post('/users/invitations/', data, format='json')
        self.assertEqual(response.status_code, 400)
