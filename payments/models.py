from django.db import models
from django.utils.translation import gettext_lazy as _
from orders.models import Order
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class Payment(models.Model):
    """
    Payment information for orders
    """
    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'credit_card', _('Credit Card')
        PAYPAL = 'paypal', _('PayPal')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        MPESA = 'mpesa', _('M-Pesa')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        AUTHORIZED = 'authorized', _('Authorized')
        PAID = 'paid', _('Paid')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')
        REFUNDED = 'refunded', _('Refunded')
        VOIDED = 'voided', _('Voided')
        FAILED = 'failed', _('Failed')

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('order')
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )
    mpesa_request_id = models.CharField(
        _('M-Pesa request ID'),
        max_length=100,
        blank=True,
        null=True
    )
    transaction_id = models.CharField(
        _('transaction ID'),
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='KSH'
    )
    method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethod.choices
    )
    status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    gateway_response = models.JSONField(
        _('gateway response'),
        default=dict,
        blank=True
    )
    is_test = models.BooleanField(
        _('is test payment'),
        default=False
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    processed_at = models.DateTimeField(
        _('processed at'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} for Order #{self.order.number}"

    def save(self, *args, **kwargs):
        if self.status == self.PaymentStatus.PAID and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)