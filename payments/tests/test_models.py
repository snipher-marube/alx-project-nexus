from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone

from orders.models import Order
from payments.models import Payment

User = get_user_model()

class PaymentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.order = Order.objects.create(user=self.user, total=Decimal('100.00'))

    def test_payment_creation(self):
        """Test payment creation"""
        payment = Payment.objects.create(
            order=self.order,
            transaction_id='test_transaction_123',
            amount=Decimal('100.00'),
            method='credit_card',
            status='paid'
        )
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.transaction_id, 'test_transaction_123')
        self.assertIsNotNone(payment.processed_at)

    def test_payment_str(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            order=self.order,
            transaction_id='test_transaction_456',
            amount=Decimal('100.00'),
            method='paypal'
        )
        expected_str = f"Payment test_transaction_456 for Order #{self.order.number}"
        self.assertEqual(str(payment), expected_str)
