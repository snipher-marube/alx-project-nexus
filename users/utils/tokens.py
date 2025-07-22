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
            str(user.is_verified) +  # Use is_verified instead of verification_token
            str(timestamp)
        )

    def check_token(self, user, token):
        """
        Check if the token is valid for the user, considering the token's age
        """
        # Ensure user and token are valid
        if not user or not token:
            logger.error("Invalid user or token for verification")
            return False
        # Check if the token matches the user's verification token
        if not constant_time_compare(user.verification_token, token):
            logger.error("Token does not match user's verification token")
            return False
        # Check if the token is still valid
        if not user.verification_token_created_at:
            logger.error("User verification token creation time is not set")
            return False
        # Ensure the token is not expired
        if not user.verification_token:
            logger.error("User verification token is not set")
            return False
        
        if not (user and token):
            return False
            
        # Check token age (e.g., 24 hours validity)
        if (timezone.now() - user.verification_token_created_at).days > 1:
            return False
            
        return super().check_token(user, token)

email_verification_token_generator = EmailVerificationTokenGenerator()