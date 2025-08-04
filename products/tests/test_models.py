from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError

from products.models import Category, Brand, Product, ProductVariant

User = get_user_model()

class CategoryModelTests(TestCase):

    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(name='Electronics', slug='electronics')
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')

    def test_category_full_path(self):
        """Test category get_full_path method"""
        parent = Category.objects.create(name='Electronics', slug='electronics')
        child = Category.objects.create(name='Laptops', slug='laptops', parent=parent)
        self.assertEqual(child.get_full_path(), 'Electronics > Laptops')


class BrandModelTests(TestCase):

    def test_brand_creation(self):
        """Test brand creation"""
        brand = Brand.objects.create(name='Apple', slug='apple')
        self.assertEqual(brand.name, 'Apple')
        self.assertEqual(brand.slug, 'apple')


class ProductModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.brand = Brand.objects.create(name='Apple', slug='apple')

    def test_product_creation(self):
        """Test product creation"""
        product = Product.objects.create(
            name='MacBook Pro',
            category=self.category,
            brand=self.brand,
            price=Decimal('1999.99'),
            created_by=self.user
        )
        self.assertEqual(product.name, 'MacBook Pro')
        self.assertTrue(product.slug.startswith('macbook-pro'))

    def test_product_in_stock(self):
        """Test is_in_stock property"""
        product = Product.objects.create(
            name='iPhone',
            category=self.category,
            price=Decimal('999.99'),
            quantity=10,
            track_quantity=True,
            created_by=self.user
        )
        self.assertTrue(product.is_in_stock)
        product.quantity = 0
        product.save()
        self.assertFalse(product.is_in_stock)

    def test_product_discount_percentage(self):
        """Test discount_percentage property"""
        product = Product.objects.create(
            name='iPad',
            category=self.category,
            price=Decimal('799.99'),
            compare_at_price=Decimal('999.99'),
            created_by=self.user
        )
        self.assertEqual(product.discount_percentage, 20.00)
