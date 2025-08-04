from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from knox.models import AuthToken

class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+254712345678',
            'user_type': 'CUSTOMER',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        self.user = User.objects.create_user(**{k: v for k, v in self.user_data.items() if k != 'password2'})

    def test_user_registration(self):
        """Test user registration view"""
        url = reverse('user-register')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(User.objects.count(), 2) # one created in setup

    def test_user_login(self):
        """Test user login view"""
        self.user.is_verified = True
        self.user.save()
        url = reverse('user-login')
        data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data['user'])

    def test_user_logout(self):
        """Test user logout view"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_all(self):
        """Test user logout from all devices view"""
        # Create a couple of tokens
        AuthToken.objects.create(user=self.user)
        AuthToken.objects.create(user=self.user)

        self.client.force_authenticate(user=self.user)
        url = reverse('user-logout-all')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AuthToken.objects.filter(user=self.user).count(), 0)

class UserProfileAPIViewTests(TestCase):
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
        self.client.force_authenticate(user=self.user)
        self.url = reverse('user-profile')

    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile(self):
        """Test updating user profile"""
        data = {'bio': 'This is a test bio.'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'This is a test bio.')

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