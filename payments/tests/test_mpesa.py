import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch

from orders.models import Order
from payments.models import Payment

User = get_user_model()

class MpesaPaymentAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.order = Order.objects.create(user=self.user, total=Decimal('100.00'))
        self.client.force_authenticate(user=self.user)
        self.mpesa_payment_url = reverse('mpesa-payment')
        self.mpesa_callback_url = reverse('mpesa-callback')

    @patch('payments.mpesa_utils.initiate_stk_push')
    def test_initiate_mpesa_payment_success(self, mock_initiate_stk_push):
        """Test initiating M-Pesa payment successfully"""
        mock_initiate_stk_push.return_value = {
            "ResponseCode": "0",
            "CheckoutRequestID": "ws_CO_1234567890"
        }

        data = {
            "phone_number": "254712345678",
            "order_id": str(self.order.id)
        }

        response = self.client.post(self.mpesa_payment_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "STK push initiated successfully.")

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.phone_number, "254712345678")
        self.assertEqual(payment.mpesa_request_id, "ws_CO_1234567890")
        self.assertEqual(payment.status, Payment.PaymentStatus.PENDING)

    @patch('payments.mpesa_utils.initiate_stk_push')
    def test_initiate_mpesa_payment_failure(self, mock_initiate_stk_push):
        """Test initiating M-Pesa payment with failure from the gateway"""
        mock_initiate_stk_push.return_value = {
            "ResponseCode": "1",
            "errorMessage": "Invalid credentials"
        }

        data = {
            "phone_number": "254712345678",
            "order_id": str(self.order.id)
        }

        response = self.client.post(self.mpesa_payment_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Failed to initiate STK push.")

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.status, Payment.PaymentStatus.FAILED)

    def test_mpesa_callback_success(self):
        """Test M-Pesa callback with a successful payment"""
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total,
            method=Payment.PaymentMethod.MPESA,
            status=Payment.PaymentStatus.PENDING,
            mpesa_request_id="ws_CO_1234567890"
        )

        callback_data = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_1234567890",
                    "ResultCode": 0,
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 100.0},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123XYZ"},
                            {"Name": "TransactionDate", "Value": "20250101120000"},
                            {"Name": "PhoneNumber", "Value": "254712345678"}
                        ]
                    }
                }
            }
        }

        response = self.client.post(self.mpesa_callback_url, callback_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PaymentStatus.PAID)
        self.assertEqual(payment.transaction_id, "ABC123XYZ")

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    def test_mpesa_callback_failure(self):
        """Test M-Pesa callback with a failed payment"""
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total,
            method=Payment.PaymentMethod.MPESA,
            status=Payment.PaymentStatus.PENDING,
            mpesa_request_id="ws_CO_0987654321"
        )

        callback_data = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_0987654321",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user."
                }
            }
        }

        response = self.client.post(self.mpesa_callback_url, callback_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PaymentStatus.FAILED)

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.FAILED)
