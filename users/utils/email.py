from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from users.utils.tokens import email_verification_token_generator
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
            # Generate token FIRST to ensure it is consistent with the user's state
            token = email_verification_token_generator.make_token(user)
            if not token:
                logger.error("Failed to generate verification token")
                raise ValidationError('Failed to generate verification token')
            # Store the token and timestamp in the user model
            user.verification_token = token
            user.verification_token_created_at = timezone.now()
            user.save(update_fields=['verification_token', 'verification_token_created_at'])    
            logger.debug(f"Generated token: {token} for user: {user.email}")
            if not user.email:
                logger.error("User email is not set")
                raise ValidationError(_('User email is not set'))
            if not user.is_active:
                logger.error("User account is not active")
                raise ValidationError(_('User account is not active'))
            
            # Build verification URL
            verification_url = request.build_absolute_uri(
                f'/api/v1/auth/verify-email/{user.id}/{token}/'
            )
            logger.debug(f"Verification URL: {verification_url}")
            
            # Prepare email context
            context = {
                'user': user,
                'verification_url': verification_url,
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
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Verification email sent to {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}", exc_info=True)
            raise ValidationError('Failed to send verification email') from e

    @staticmethod
    def verify_token(user_id, token):
        """
        More robust verification process
        """
        try:
            user = User.objects.get(pk=user_id)
            
            if user.is_verified:
                logger.warning("User already verified")
                return user  # Consider this success case
                
            if not user.verification_token:
                logger.error("No verification token exists")
                raise ValidationError('No verification token exists')
                
            # Critical debug logs
            logger.debug(f"Stored token: {user.verification_token}")
            logger.debug(f"Provided token: {token}")
            logger.debug(f"Token created at: {user.verification_token_created_at}")
            
            if not email_verification_token_generator.check_token(user, token):
                logger.error("Token validation failed")
                raise ValidationError('Invalid or expired verification token')
                
            # Mark as verified
            user.is_verified = True
            user.verification_token = None
            user.verification_token_created_at = None
            user.save()
            
            logger.info("User successfully verified")
            return user
            
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            raise ValidationError('Invalid user ID')
        except Exception as e:
            logger.error(f"Verification error: {str(e)}", exc_info=True)
            raise ValidationError('Verification failed') from e