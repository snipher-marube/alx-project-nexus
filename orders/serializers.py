from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from products.models import Product, ProductVariant
from products.serializers import ProductSerializer, ProductVariantSerializer
from payments.serializers import PaymentSerializer
from .models import (
    Order, OrderItem, ShippingAddress, BillingAddress,
    OrderStatusHistory, Cart, CartItem
)


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ['order']
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True}
        }


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        exclude = ['order']
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=False,
        allow_null=True
    )
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        write_only=True,
        required=False,
        allow_null=True
    )
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'sku', 'name', 'price', 'discount_amount', 'quantity',
            'tax', 'total_price', 'metadata', 'created_at'
        ]
        read_only_fields = ['sku', 'name', 'price', 'tax']

    def validate(self, data):
        if not data.get('product') and not data.get('variant'):
            raise serializers.ValidationError(
                _("Either product or variant must be specified.")
            )
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    shipping_address = ShippingAddressSerializer(required=False)
    billing_address = BillingAddressSerializer(required=False)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    item_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'user', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'currency', 'subtotal', 'tax',
            'shipping_cost', 'discount', 'total', 'items', 'item_count',
            'shipping_address', 'billing_address', 'customer_notes',
            'admin_notes', 'ip_address', 'created_at', 'updated_at',
            'paid_at', 'cancelled_at', 'payments'
        ]
        read_only_fields = [
            'number', 'subtotal', 'tax', 'discount', 'total',
            'item_count', 'paid_at', 'cancelled_at', 'payments'
        ]

    def create(self, validated_data):
        with transaction.atomic():
            items_data = validated_data.pop('items', [])
            shipping_address_data = validated_data.pop('shipping_address', None)
            billing_address_data = validated_data.pop('billing_address', None)
            
            # Set default status for new orders
            validated_data.setdefault('status', Order.OrderStatus.PENDING)
            
            # Get IP address from request if available
            request = self.context.get('request')
            if request:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
            order = Order.objects.create(**validated_data)
            
            # Create order items
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
            
            # Create addresses if provided
            if shipping_address_data:
                ShippingAddress.objects.create(
                    order=order,
                    **shipping_address_data
                )
            
            if billing_address_data:
                BillingAddress.objects.create(
                    order=order,
                    **billing_address_data
                )
            
            # Recalculate totals
            order.calculate_totals()
            order.save()
            
            return order


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    old_status_display = serializers.CharField(
        source='get_old_status_display',
        read_only=True
    )
    new_status_display = serializers.CharField(
        source='get_new_status_display',
        read_only=True
    )
    created_by = serializers.StringRelatedField()

    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'note',
            'created_by', 'created_at'
        ]
        read_only_fields = fields





class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=False,
        allow_null=True
    )
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        write_only=True,
        required=False,
        allow_null=True
    )
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'price', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['price', 'total_price', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('product') and not data.get('variant'):
            raise serializers.ValidationError(
                _("Either product or variant must be specified.")
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'items',
            'subtotal', 'total_items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'session_key', 'subtotal',
            'total_items', 'created_at', 'updated_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    shipping_address = ShippingAddressSerializer(required=True)
    billing_address = BillingAddressSerializer(required=False)
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        required=True
    )
    mpesa_phone_number = serializers.CharField(required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    use_shipping_as_billing = serializers.BooleanField(default=False)

    def validate(self, data):
        if data.get('use_shipping_as_billing') and data.get('billing_address'):
            raise serializers.ValidationError(
                _("Cannot specify both billing_address and use_shipping_as_billing=True")
            )

        payment_method = data.get('payment_method')
        mpesa_phone_number = data.get('mpesa_phone_number')

        if payment_method == Order.PaymentMethod.MPESA and not mpesa_phone_number:
            raise serializers.ValidationError({
                'mpesa_phone_number': _('This field is required for M-Pesa payments.')
            })

        return data