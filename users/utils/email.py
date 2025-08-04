from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.exceptions import ValidationError
from users.models import User
from .tokens import email_verification_token_generator
import logging

logger = logging.getLogger(__name__)

class EmailVerification:
    @staticmethod
    def send_verification_email(user, request):
        """
        Send email verification link to user with enhanced error handling
        """
        try:
            token = email_verification_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            verification_url = request.build_absolute_uri(
                f'/api/v1/auth/verify-email/{uid}/{token}/'
            )
            
            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': settings.SITE_NAME
            }

            subject = 'Verify your email address'
            html_message = render_to_string('emails/verification_email.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
                reply_to=[settings.REPLY_TO_EMAIL],
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Verification email sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}", exc_info=True)
            raise ValidationError('Failed to send verification email') from e

    @staticmethod
    def verify_token(uidb64, token):
        """
        Verify the email verification token.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and email_verification_token_generator.check_token(user, token):
            if user.is_verified:
                logger.warning("User already verified")
                return user
            
            user.is_verified = True
            user.save()
            logger.info("User successfully verified")
            return user
        else:
            logger.error("Token validation failed")
            raise ValidationError('Invalid or expired verification token')