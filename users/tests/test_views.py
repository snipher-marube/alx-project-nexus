from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User

class EmailVerificationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )
        self.verification_url = reverse('verify-email', args=[str(self.user.id), 'token'])

    def test_verification_success(self):
        """Test successful email verification through API"""
        # Generate valid token
        from users.utils.tokens import email_verification_token_generator
        token = email_verification_token_generator.make_token(self.user)
        self.user.verification_token = token
        self.user.save()

        # Call verification endpoint
        url = reverse('verify-email', args=[str(self.user.id), token])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_verified)

    def test_verification_invalid_token(self):
        """Test verification with invalid token"""
        response = self.client.get(self.verification_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_resend_verification_email(self):
        """Test resend verification email endpoint"""
        self.client.force_authenticate(user=self.user)
        url = reverse('resend-verification')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)