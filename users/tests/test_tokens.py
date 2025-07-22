from django.test import TestCase
from django.utils import timezone
from users.models import User
from users.utils.tokens import email_verification_token_generator

class EmailVerificationTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )

    def test_token_generation_and_validation(self):
        """Test that tokens can be generated and validated correctly"""
        # Generate token
        token = email_verification_token_generator.make_token(self.user)
        
        # Verify token works
        self.assertTrue(
            email_verification_token_generator.check_token(self.user, token),
            "Generated token should validate successfully"
        )

    def test_invalid_token(self):
        """Test that invalid tokens are rejected"""
        token = email_verification_token_generator.make_token(self.user)
        self.assertFalse(
            email_verification_token_generator.check_token(self.user, token + 'invalid'),
            "Modified tokens should be invalid"
        )

    def test_token_for_different_user(self):
        """Test that tokens are user-specific"""
        other_user = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            phone='+254798765432',
            user_type='CUSTOMER',
            password='testpass123'
        )
        token = email_verification_token_generator.make_token(self.user)
        self.assertFalse(
            email_verification_token_generator.check_token(other_user, token),
            "Tokens should be user-specific"
        )

    def test_token_after_verification(self):
        """Test that tokens become invalid after verification"""
        token = email_verification_token_generator.make_token(self.user)
        self.user.is_verified = True
        self.user.save()
        self.assertFalse(
            email_verification_token_generator.check_token(self.user, token),
            "Tokens should be invalid after verification"
        )