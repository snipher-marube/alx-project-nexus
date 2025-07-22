from django.contrib.auth.tokens import PasswordResetTokenGenerator
import hashlib

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + 
            str(user.is_verified) + str(user.verification_token)
        )

email_verification_token_generator = EmailVerificationTokenGenerator()