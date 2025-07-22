from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """
        Hash value components must be consistent with user state at generation time
        """
        return (
            str(user.pk) + 
            str(user.verification_token) +  # Critical - must match what's saved
            str(timestamp) + 
            str(user.is_verified)
        )

    def check_token(self, user, token):
        """
        Simplified token validation that ensures consistency
        """
        if not (user and token):
            logger.error("Missing user or token")
            return False
            
        if not user.verification_token:
            logger.error("No verification token stored for user")
            return False
            
        # Use parent class's validation which handles the secret properly
        return super().check_token(user, token)

email_verification_token_generator = EmailVerificationTokenGenerator()