from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from products.models import Product, Category, ProductVariant
from orders.models import Cart, CartItem

User = get_user_model()


class CartModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
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

    def test_create_cart_for_user(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertIsNone(self.cart.session_key)
        self.assertEqual(str(self.cart), f"Cart for {self.user.email}")

    def test_create_anonymous_cart(self):
        cart = Cart.objects.create(session_key='test_session_key')
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, 'test_session_key')
        self.assertEqual(str(cart), "Anonymous Cart (test_session_key)")

    def test_cart_properties_empty(self):
        self.assertTrue(self.cart.is_empty)
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.subtotal, Decimal('0.00'))

    def test_cart_properties_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=1)

        self.assertFalse(self.cart.is_empty)
        self.assertEqual(self.cart.total_items, 3)
        expected_subtotal = (self.product.price * 2) + self.variant.price
        self.assertEqual(self.cart.subtotal, expected_subtotal)

    def test_add_item_to_cart(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertEqual(item.cart, self.cart)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, self.product.price)
        self.assertEqual(self.cart.items.count(), 1)

    def test_add_variant_to_cart(self):
        item = CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=1)
        self.assertEqual(item.cart, self.cart)
        self.assertEqual(item.variant, self.variant)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, self.variant.price)
        self.assertEqual(self.cart.items.count(), 1)

    def test_cart_item_total_price(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(item.total_price, self.product.price * 3)

    def test_cart_item_uniqueness(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_cart_item_uniqueness_with_variant(self):
        CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=1)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=2)

    def test_cart_item_clean_no_product_or_variant(self):
        item = CartItem(cart=self.cart, quantity=1)
        with self.assertRaises(ValidationError):
            item.clean()

    def test_cart_item_clean_both_product_and_variant(self):
        item = CartItem(cart=self.cart, product=self.product, variant=self.variant, quantity=1)
        with self.assertRaises(ValidationError):
            item.clean()

    def test_cart_item_str(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertEqual(str(item), f"1 x {self.product.name}")

    def test_cart_item_str_variant(self):
        item = CartItem.objects.create(cart=self.cart, variant=self.variant, quantity=1)
        self.assertEqual(str(item), f"1 x {self.variant.product.name} - {self.variant.name}")
