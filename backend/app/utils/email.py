# utils/email.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_invite_email(to_email, invite_url):
    subject = "You're Invited to Join Turntable"
    context = {
        'invite_url': invite_url,
    }
    message = render_to_string('emails/invite_email.html', context)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
        html_message=message
    )
