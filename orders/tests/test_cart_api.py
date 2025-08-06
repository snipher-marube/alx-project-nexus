from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from products.models import Product, Category, ProductVariant
from orders.models import Cart, CartItem

User = get_user_model()


class CartAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Laptop',
            category=self.category,
            price=Decimal('1200.00'),
            stock_quantity=10
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name='16GB RAM',
            price=Decimal('1300.00'),
            stock_quantity=5
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_get_cart(self):
        url = reverse('cart-detail', args=[self.cart.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.pk)

    def test_add_item_to_cart(self):
        url = reverse('cart-item-list')
        data = {'product': self.product.pk, 'quantity': 2}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 2)

    def test_add_variant_to_cart(self):
        url = reverse('cart-item-list')
        data = {'variant': self.variant.pk, 'quantity': 1}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().variant, self.variant)

    def test_update_cart_item(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        url = reverse('cart-item-detail', args=[item.pk])
        data = {'quantity': 3}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_delete_cart_item(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        url = reverse('cart-item-detail', args=[item.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_empty_cart(self):
        url = reverse('cart-checkout', args=[self.cart.pk])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        url = reverse('cart-checkout', args=[self.cart.pk])
        data = {
            "payment_method": "credit_card",
            "shipping_address": {
                "first_name": "Test",
                "last_name": "User",
                "address_line_1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "12345",
                "country": "US",
                "phone": "555-555-5555",
                "email": "test@example.com"
            },
            "use_shipping_as_billing": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.cart.is_empty)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(len(response.data['items']), 1)
