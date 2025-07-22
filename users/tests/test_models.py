from django.test import TestCase
from users.models import User

class UserModelTests(TestCase):
    def test_user_creation(self):
        """Test user creation with required fields"""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_verified)

    def test_username_generation(self):
        """Test automatic username generation"""
        user = User.objects.create_user(
            email='test.user@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )
        self.assertTrue(user.username.startswith('test_user'))

class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test profile is automatically created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)