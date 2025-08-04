from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from products.models import Product, Category, Brand, ProductVariant

User = get_user_model()

class ProductAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.brand = Brand.objects.create(name='Apple', slug='apple')
        self.product = Product.objects.create(
            name='MacBook Pro',
            slug='macbook-pro',
            category=self.category,
            brand=self.brand,
            price=Decimal('1999.99'),
            created_by=self.user,
            status='active'
        )

    def test_get_product_list(self):
        """Test getting a list of products"""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_product_detail(self):
        """Test getting a single product"""
        url = reverse('product-detail', args=[self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_get_category_list(self):
        """Test getting a list of categories"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_category_detail(self):
        """Test getting a single category"""
        url = reverse('category-detail', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_get_brand_list(self):
        """Test getting a list of brands"""
        url = reverse('brand-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_brand_detail(self):
        """Test getting a single brand"""
        url = reverse('brand-detail', args=[self.brand.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.brand.name)
