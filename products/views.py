from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Count, Avg
from django.shortcuts import get_object_or_404

from .models import (
    Category, Brand, Product, ProductImage,
    ProductVariant, ProductAttribute,
    ProductAttributeValue, ProductVariantAttribute,
    ProductReview, ProductSpecification
)
from .serializers import (
    CategorySerializer, BrandSerializer,
    ProductSerializer, ProductListSerializer,
    ProductImageSerializer, ProductVariantSerializer,
    ProductAttributeSerializer, ProductAttributeValueSerializer,
    ProductVariantAttributeSerializer, ProductReviewSerializer,
    ProductSpecificationSerializer, ProductDetailSerializer
)
from .filters import ProductFilter, CategoryFilter, ProductVariantFilter
from .pagination import OptimizedPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(
        product_count=Count('products', distinct=True)
    ).prefetch_related('children')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'product_count', 'created_at']
    ordering = ['name']
    pagination_class = OptimizedPagination
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), DjangoModelPermissions()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by parent for hierarchical listing
        parent_slug = self.request.query_params.get('parent')
        if parent_slug:
            parent = get_object_or_404(Category, slug=parent_slug)
            queryset = queryset.filter(parent=parent)
        else:
            # Only root categories by default
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset

    @action(detail=True, methods=['get'])
    def children(self, request, slug=None):
        category = self.get_object()
        children = category.children.annotate(
            product_count=Count('products', distinct=True)
        )
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.annotate(
        product_count=Count('products', distinct=True)
    )
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'product_count', 'created_at']
    ordering = ['name']
    pagination_class = OptimizedPagination
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), DjangoModelPermissions()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'brand'
    ).prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.order_by('order')),
        Prefetch('variants', queryset=ProductVariant.objects.prefetch_related(
            'attributes__attribute',
            'attributes__value'
        )),
        Prefetch('specifications', queryset=ProductSpecification.objects.order_by('order')),
        Prefetch('reviews', queryset=ProductReview.objects.filter(is_approved=True))
    ).annotate(
        calculated_avg_rating=Avg('reviews__rating')
    )
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = [
        'name', 'description', 'sku', 'barcode',
        'category__name', 'brand__name'
    ]
    ordering_fields = [
        'name', 'price', 'average_rating', 'created_at',
        'updated_at', 'published_at'
    ]
    ordering = ['-created_at']
    pagination_class = OptimizedPagination
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), DjangoModelPermissions()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status (only active products for non-staff)
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='active')
        
        return queryset

    @action(detail=True, methods=['post'])
    def add_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(
            data=request.data,
            context={'product': product}
        )
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        product = self.get_object()
        serializer = ProductReviewSerializer(
            data=request.data,
            context={
                'product': product,
                'request': request
            }
        )
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = OptimizedPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        product_slug = self.request.query_params.get('product')
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        return queryset.order_by('order')


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').prefetch_related(
        'attributes__attribute',
        'attributes__value'
    )
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductVariantFilter
    search_fields = ['name', 'sku', 'product__name']
    ordering_fields = ['name', 'price', 'quantity', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = OptimizedPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        product_slug = self.request.query_params.get('product')
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        return queryset


class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.prefetch_related('values')
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = OptimizedPagination


class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeValue.objects.select_related('attribute')
    serializer_class = ProductAttributeValueSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['attribute']
    search_fields = ['value']
    ordering_fields = ['value', 'created_at']
    ordering = ['value']
    pagination_class = OptimizedPagination


class ProductVariantAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductVariantAttribute.objects.select_related(
        'variant', 'attribute', 'value'
    )
    serializer_class = ProductVariantAttributeSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['variant', 'attribute', 'value']
    pagination_class = OptimizedPagination


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'user', 'is_approved', 'rating']
    search_fields = ['title', 'comment']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    pagination_class = OptimizedPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), DjangoModelPermissions()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For non-staff users, only show approved reviews
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductSpecificationViewSet(viewsets.ModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    ordering = ['order']
    pagination_class = OptimizedPagination
