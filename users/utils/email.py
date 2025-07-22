import uuid
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from .tokens import email_verification_token_generator
from users.models import User

class EmailVerification:
    @staticmethod
    def send_verification_email(user, request):
        """
        Send email verification link to user
        """
        # Generate token and set expiration (24 hours)
        token = email_verification_token_generator.make_token(user)
        user.verification_token = token
        user.verification_token_created_at = timezone.now()
        user.save()

        # Prepare email context
        context = {
            'user': user,
            'verification_url': request.build_absolute_uri(
                f'/api/v1/auth/verify-email/{user.id}/{token}/'
            ),
            'site_name': settings.SITE_NAME
        }

        # Render email templates
        subject = 'Verify your email address'
        html_message = render_to_string('emails/verification_email.html', context)
        plain_message = strip_tags(html_message)

        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[settings.REPLY_TO_EMAIL],
            headers={
                'X-Priority': '1',
                'X-MSMail-Priority': 'High',
                'X-Mailer': 'Django',
                'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',
            }
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

    @staticmethod
    def verify_token(user_id, token):
        """
        Verify the email verification token
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError('Invalid user ID')

        # Check if token is valid and not expired
        if not email_verification_token_generator.check_token(user, token):
            raise ValidationError('Invalid or expired verification token')

        # Check if token was created more than 24 hours ago
        if (timezone.now() - user.verification_token_created_at).total_seconds() > 86400:
            raise ValidationError('Verification link has expired')

        # Mark user as verified and clear token
        user.is_verified = True
        user.verification_token = None
        user.verification_token_created_at = None
        user.save()

        return user