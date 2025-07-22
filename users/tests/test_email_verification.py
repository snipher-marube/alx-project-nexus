from django.test import TestCase, RequestFactory
from django.core import mail
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from users.utils.email import EmailVerification, email_verification_token_generator

class EmailVerificationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )
        self.request = self.factory.get('/')

    def test_send_verification_email(self):
        """Test that verification emails are sent correctly"""
        # Send verification email
        result = EmailVerification.send_verification_email(self.user, self.request)
        self.assertTrue(result, "Email sending should return True on success")
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1, "Email should be in outbox")
        self.assertIn('Verify your email address', mail.outbox[0].subject)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_verify_token_success(self):
        """Test successful token verification"""
        # Generate and save token
        token = email_verification_token_generator.make_token(self.user)
        self.user.verification_token = token
        self.user.verification_token_created_at = timezone.now()
        self.user.save()

        # Verify token
        verified_user = EmailVerification.verify_token(self.user.id, token)
        self.assertEqual(verified_user, self.user, "Should return the verified user")
        self.assertTrue(verified_user.is_verified, "User should be marked as verified")
        self.assertIsNone(verified_user.verification_token, "Token should be cleared after verification")

    def test_verify_invalid_token(self):
        """Test verification with invalid token"""
        with self.assertRaises(ValidationError):
            EmailVerification.verify_token(self.user.id, 'invalid-token')

    def test_verify_already_verified(self):
        """Test verification when user is already verified"""
        self.user.is_verified = True
        self.user.save()
        
        # Should still return user without error
        user = EmailVerification.verify_token(self.user.id, 'any-token')
        self.assertEqual(user, self.user)