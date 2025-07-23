from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.text import slugify
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Category, Brand, Product, ProductImage,
    ProductVariant, ProductAttribute,
    ProductAttributeValue, ProductVariantAttribute,
    ProductReview, ProductSpecification
)


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    full_path = serializers.CharField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'description',
            'is_active', 'full_path', 'product_count',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'slug': {
                'validators': [
                    UniqueValidator(queryset=Category.objects.all())
                ]
            }
        }

    def validate_parent(self, value):
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value

    def create(self, validated_data):
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'logo_url',
            'is_active', 'website', 'product_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'slug': {
                'validators': [
                    UniqueValidator(queryset=Brand.objects.all())
                ]
            },
            'logo': {'write_only': True}
        }

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None

    def create(self, validated_data):
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'image_url', 'thumbnail_url',
            'alt_text', 'is_primary', 'order', 'created_at'
        ]
        extra_kwargs = {
            'image': {'write_only': True},
            'product': {'write_only': True}
        }

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.image:
            # In production, you'd generate a thumbnail URL here
            # For now, just return the image URL
            return obj.image.url
        return None


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'value', 'slug', 'created_at', 'updated_at']


class ProductAttributeSerializer(serializers.ModelSerializer):
    values = ProductAttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'slug', 'description', 'values', 'created_at', 'updated_at']


class ProductVariantAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField(slug_field='name', queryset=ProductAttribute.objects.all())
    value = serializers.SlugRelatedField(slug_field='value', queryset=ProductAttributeValue.objects.all())

    class Meta:
        model = ProductVariantAttribute
        fields = ['id', 'attribute', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = ProductVariantAttributeSerializer(many=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'name', 'sku', 'price', 'compare_at_price',
            'quantity', 'track_quantity', 'weight', 'attributes', 'in_stock',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'product': {'required': False}
        }

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        variant = ProductVariant.objects.create(**validated_data)
        
        for attr_data in attributes_data:
            ProductVariantAttribute.objects.create(variant=variant, **attr_data)
        
        return variant

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', None)
        
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            
            if attributes_data is not None:
                instance.attributes.all().delete()
                for attr_data in attributes_data:
                    ProductVariantAttribute.objects.create(variant=instance, **attr_data)
        
        return instance


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ['id', 'product', 'name', 'value', 'order']
        extra_kwargs = {
            'product': {'required': False}
        }


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'username', 'user_email',
            'rating', 'title', 'comment', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_approved']
        extra_kwargs = {
            'product': {'required': False}
        }

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True,
        required=False,
        allow_null=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    average_rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    inventory_status = serializers.CharField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_id',
            'brand', 'brand_id', 'status', 'price', 'compare_at_price',
            'discount_percentage', 'cost_per_item', 'sku', 'barcode',
            'quantity', 'track_quantity', 'inventory_status', 'is_in_stock',
            'continue_selling_when_out_of_stock', 'weight', 'is_featured',
            'is_digital', 'requires_shipping', 'primary_image', 'images',
            'variants', 'specifications', 'reviews', 'average_rating',
            'published_at', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'slug': {
                'required': False,
                'validators': [
                    UniqueValidator(queryset=Product.objects.all())
                ]
            }
        }

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

    def create(self, validated_data):
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        
        # Handle the case where slug might still not be unique
        base_slug = validated_data['slug']
        counter = 1
        while Product.objects.filter(slug=validated_data['slug']).exists():
            validated_data['slug'] = f"{base_slug}-{counter}"
            counter += 1
        
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    average_rating = serializers.DecimalField(
        source='calculated_avg_rating',
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    inventory_status = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_at_price',
            'discount_percentage', 'primary_image', 'average_rating',
            'inventory_status', 'is_featured', 'created_at'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None
    
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    average_rating = serializers.SerializerMethodField()
    inventory_status = serializers.CharField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'brand',
            'status', 'price', 'compare_at_price', 'discount_percentage',
            'cost_per_item', 'sku', 'barcode', 'quantity', 'track_quantity',
            'inventory_status', 'is_in_stock', 'continue_selling_when_out_of_stock',
            'weight', 'is_featured', 'is_digital', 'requires_shipping',
            'primary_image', 'images', 'variants', 'specifications', 'reviews',
            'average_rating', 'published_at', 'created_at', 'updated_at'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

    def get_average_rating(self, obj):
        return obj.average_rating  # This uses the property from the model