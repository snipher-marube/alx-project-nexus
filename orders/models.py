import uuid
import logging
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from django.conf import settings
from products.models import Product, ProductVariant
from decimal import Decimal

User = settings.AUTH_USER_MODEL


class Order(models.Model):
    """
    Core order model representing a customer's purchase
    """
    class OrderStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending Payment')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
        FAILED = 'failed', _('Failed')
        ON_HOLD = 'on_hold', _('On Hold')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        AUTHORIZED = 'authorized', _('Authorized')
        PAID = 'paid', _('Paid')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')
        REFUNDED = 'refunded', _('Refunded')
        VOIDED = 'voided', _('Voided')
        FAILED = 'failed', _('Failed')

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'credit_card', _('Credit Card')
        PAYPAL = 'paypal', _('PayPal')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        COD = 'cod', _('Cash on Delivery')
        WALLET = 'wallet', _('Wallet')
        MPESA = 'mpesa', _('M-Pesa')
        STRIPE = 'stripe', _('Stripe')
        OTHER = 'other', _('Other')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name=_('user')
    )
    number = models.CharField(
        _('order number'),
        max_length=32,
        unique=True,
        editable=False
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD'
    )
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    tax = models.DecimalField(
        _('tax amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    shipping_cost = models.DecimalField(
        _('shipping cost'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    discount = models.DecimalField(
        _('discount amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('total amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    customer_notes = models.TextField(
        _('customer notes'),
        blank=True
    )
    admin_notes = models.TextField(
        _('admin notes'),
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    paid_at = models.DateTimeField(
        _('paid at'),
        null=True,
        blank=True
    )
    cancelled_at = models.DateTimeField(
        _('cancelled at'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order #{self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_order_number()
        self.calculate_totals()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number with timestamp and random component"""
        while True:
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            random_part = uuid.uuid4().hex[:6].upper()
            order_number = f"ORD-{timestamp}-{random_part}"
            logging.info(f"Generated order number: {order_number}")
            if not Order.objects.filter(number=order_number).exists():
                logging.info(f"Using order number: {order_number}")
                return order_number
            logging.warning(f"Duplicate order number detected: {order_number}")

    def calculate_totals(self):
        """
        Calculate order totals based on line items
        """
        if self.pk:
            aggregates = self.items.aggregate(
                subtotal=Sum(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                ),
                discount=Sum(
                    F('discount_amount') * F('quantity'),
                    output_field=DecimalField()
                )
            )
            self.subtotal = aggregates['subtotal'] or Decimal('0.00')
            self.discount = aggregates['discount'] or Decimal('0.00')
            self.total = self.subtotal + self.tax + self.shipping_cost - self.discount

    @property
    def item_count(self):
        """Total quantity of items in the order"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    def clean(self):
        if self.status == self.OrderStatus.CANCELLED and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        if self.payment_status == self.PaymentStatus.PAID and not self.paid_at:
            self.paid_at = timezone.now()

    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status not in [
            self.OrderStatus.CANCELLED,
            self.OrderStatus.REFUNDED,
            self.OrderStatus.DELIVERED
        ]

    def cancel(self, reason=None):
        """Cancel the order"""
        if not self.can_cancel():
            raise ValidationError(_("This order cannot be cancelled."))
        
        self.status = self.OrderStatus.CANCELLED
        self.cancelled_at = timezone.now()
        if reason:
            self.admin_notes = f"Cancellation reason: {reason}\n{self.admin_notes}"
        self.save()

        # Restore inventory
        for item in self.items.all():
            if item.variant:
                item.variant.increase_inventory(item.quantity)
            elif item.product:
                item.product.increase_inventory(item.quantity)


class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('product'),
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('variant'),
        null=True,
        blank=True
    )
    sku = models.CharField(
        _('SKU'),
        max_length=100,
        blank=True
    )
    name = models.CharField(
        _('item name'),
        max_length=255
    )
    price = models.DecimalField(
        _('unit price'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        _('discount amount per unit'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        validators=[MinValueValidator(1)],
        default=1
    )
    tax = models.DecimalField(
        _('tax amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.name} (Order #{self.order.number})"

    def clean(self):
        if not self.product and not self.variant:
            raise ValidationError(_("An order item must have either a product or variant."))
        if self.product and self.variant:
            raise ValidationError(_("An order item cannot have both a product and variant."))
    
        if not self.name:
            if self.product:
                self.name = self.product.name
            elif self.variant:
                self.name = f"{self.variant.product.name} - {self.variant.name}"
    
        if not self.sku:
            if self.product and self.product.sku:
                self.sku = self.product.sku
            elif self.variant and self.variant.sku:
                self.sku = self.variant.sku
    
        # Ensure numeric fields have values
        if self.price is None:
            self.price = Decimal('0.00')
        if self.discount_amount is None:
            self.discount_amount = Decimal('0.00')
        if self.quantity is None:
            self.quantity = 1
    
        # Validate price after discount
        if (self.price - self.discount_amount) < Decimal('0.00'):
            raise ValidationError(_("Price after discount cannot be negative."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return (self.price - self.discount_amount) * self.quantity

    @property
    def actual_product(self):
        """Return the actual product (either from product or variant)"""
        return self.variant.product if self.variant else self.product


class ShippingAddress(models.Model):
    """
    Shipping address for an order
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='shipping_address',
        verbose_name=_('order')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=100
    )
    last_name = models.CharField(
        _('last name'),
        max_length=100
    )
    company = models.CharField(
        _('company'),
        max_length=100,
        blank=True
    )
    address_line_1 = models.CharField(
        _('address line 1'),
        max_length=255
    )
    address_line_2 = models.CharField(
        _('address line 2'),
        max_length=255,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=100
    )
    state = models.CharField(
        _('state/province'),
        max_length=100
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20
    )
    country = models.CharField(
        _('country'),
        max_length=100
    )
    phone = models.CharField(
        _('phone number'),
        max_length=30
    )
    email = models.EmailField(
        _('email address')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('shipping address')
        verbose_name_plural = _('shipping addresses')

    def __str__(self):
        return f"Shipping Address for Order #{self.order.number}"

    def get_full_address(self):
        """Return formatted full address"""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.country,
            self.postal_code
        ]
        return ', '.join(filter(None, parts))


class BillingAddress(models.Model):
    """
    Billing address for an order
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='billing_address',
        verbose_name=_('order')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=100
    )
    last_name = models.CharField(
        _('last name'),
        max_length=100
    )
    company = models.CharField(
        _('company'),
        max_length=100,
        blank=True
    )
    address_line_1 = models.CharField(
        _('address line 1'),
        max_length=255
    )
    address_line_2 = models.CharField(
        _('address line 2'),
        max_length=255,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=100
    )
    state = models.CharField(
        _('state/province'),
        max_length=100
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20
    )
    country = models.CharField(
        _('country'),
        max_length=100
    )
    phone = models.CharField(
        _('phone number'),
        max_length=30
    )
    email = models.EmailField(
        _('email address')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('billing address')
        verbose_name_plural = _('billing addresses')

    def __str__(self):
        return f"Billing Address for Order #{self.order.number}"

    def get_full_address(self):
        """Return formatted full address"""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.country,
            self.postal_code
        ]
        return ', '.join(filter(None, parts))


class OrderStatusHistory(models.Model):
    """
    Track changes to order status over time
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('order')
    )
    old_status = models.CharField(
        _('old status'),
        max_length=20,
        choices=Order.OrderStatus.choices,
        null=True,
        blank=True
    )
    new_status = models.CharField(
        _('new status'),
        max_length=20,
        choices=Order.OrderStatus.choices
    )
    note = models.TextField(
        _('note'),
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('order status history')
        verbose_name_plural = _('order status histories')
        ordering = ['-created_at']

    def __str__(self):
        return f"Status change for Order #{self.order.number}"





class Cart(models.Model):
    """
    Shopping cart model
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_('user'),
        null=True,
        blank=True
    )
    session_key = models.CharField(
        _('session key'),
        max_length=40,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"

    @property
    def is_empty(self):
        return self.items.count() == 0

    @property
    def total_items(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    @property
    def subtotal(self):
        subtotal = self.items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or Decimal('0.00')
        return subtotal


class CartItem(models.Model):
    """
    Items in a shopping cart
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('cart')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_('product'),
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_('variant'),
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        _('price'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        unique_together = [['cart', 'product', 'variant']]

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name}"
        return f"{self.quantity} x {self.variant.product.name} - {self.variant.name}"

    def clean(self):
        if not self.product and not self.variant:
            raise ValidationError(_("A cart item must have either a product or variant."))
        if self.product and self.variant:
            raise ValidationError(_("A cart item cannot have both a product and variant."))

    def save(self, *args, **kwargs):
        self.clean()
        if not self.price:
            if self.product:
                self.price = self.product.price
            elif self.variant:
                self.price = self.variant.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price * self.quantity