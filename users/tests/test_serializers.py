from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ProfileSerializer,
)
from users.models import User

class UserRegistrationSerializerTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_valid_registration(self):
        """Test successful user registration with valid data"""
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+254711223344',
            'user_type': 'CUSTOMER',
            'password': 'password123',
            'password2': 'password123',
        }
        serializer = UserRegistrationSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, data['email'])

    def test_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password456',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+254712345678',
            'user_type': 'CUSTOMER',
        }
        serializer = UserRegistrationSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('password', context.exception.detail)


class UserLoginSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            is_verified=True
        )

    def test_valid_login(self):
        """Test successful login with valid credentials"""
        data = {'email': 'test@example.com', 'password': 'password123'}
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_password(self):
        """Test login with invalid password"""
        data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        serializer = UserLoginSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_unverified_user(self):
        """Test login with unverified user"""
        self.user.is_verified = False
        self.user.save()
        data = {'email': 'test@example.com', 'password': 'password123'}
        serializer = UserLoginSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

class ProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
        )

    def test_profile_serialization(self):
        """Test profile serializer returns correct data"""
        serializer = ProfileSerializer(instance=self.user.profile)
        data = serializer.data
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertIn('age', data)
