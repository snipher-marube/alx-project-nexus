from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory

@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """
    Track order status changes and update timestamps
    """
    if instance.pk:
        original = Order.objects.get(pk=instance.pk)
        
        # Check if status changed
        if original.status != instance.status:
            OrderStatusHistory.objects.create(
                order=instance,
                old_status=original.status,
                new_status=instance.status,
                created_by=getattr(instance, '_updated_by', None)
            )
        
        # Check if payment status changed to paid
        if (original.payment_status != instance.payment_status and 
            instance.payment_status == Order.PaymentStatus.PAID):
            instance.paid_at = timezone.now()