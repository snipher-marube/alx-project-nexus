from django.test import TestCase
from users.models import User, Profile
from django.core.exceptions import ValidationError
from datetime import date

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

    def test_unique_username_generation(self):
        """Test that generated usernames are unique"""
        User.objects.create_user(
            email='test.user@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345678',
            user_type='CUSTOMER',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            email='test.user2@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345679',
            user_type='CUSTOMER',
            password='testpass123'
        )
        user2.username = 'test_user'
        user2.save()

        user3 = User.objects.create_user(
            email='test.user@example.com',
            first_name='Test',
            last_name='User',
            phone='+254712345610',
            user_type='CUSTOMER',
            password='testpass123'
        )
        self.assertNotEqual(user3.username, 'test_user')


    def test_user_clean_method(self):
        """Test user clean method raises validation error"""
        with self.assertRaises(ValidationError):
            user = User(email='test@example.com', phone='+254712345678', user_type='CUSTOMER')
            user.clean()


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
        self.profile = self.user.profile

    def test_profile_creation(self):
        """Test profile is automatically created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)

    def test_profile_age(self):
        """Test profile age calculation"""
        self.profile.date_of_birth = date(2000, 1, 1)
        self.profile.save()
        self.assertEqual(self.profile.age, 25)

    def test_profile_get_full_address(self):
        """Test profile get_full_address method"""
        self.profile.address = '123 Main St'
        self.profile.city = 'Anytown'
        self.profile.state = 'CA'
        self.profile.country = 'US'
        self.profile.postal_code = '12345'
        self.profile.save()
        expected_address = '123 Main St, Anytown, CA, US, 12345'
        self.assertEqual(self.profile.get_full_address(), expected_address)