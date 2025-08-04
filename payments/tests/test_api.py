from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from orders.models import Order
from payments.models import Payment

User = get_user_model()

class PaymentAPITests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='password')
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.order = Order.objects.create(user=self.user, total=Decimal('100.00'))
        self.payment = Payment.objects.create(
            order=self.order,
            transaction_id='test_transaction_123',
            amount=Decimal('100.00'),
            method='credit_card',
            status='paid'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_get_payment_list(self):
        """Test getting a list of payments"""
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_payment_detail(self):
        """Test getting a single payment"""
        url = reverse('payment-detail', args=[self.payment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], self.payment.transaction_id)

    def test_get_payment_list_not_admin(self):
        """Test that non-admin users cannot list payments"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
