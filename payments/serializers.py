from rest_framework import serializers
from .models import Payment
from django.utils.translation import gettext_lazy as _

class PaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(
        source='get_method_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'amount', 'currency',
            'method', 'method_display', 'status', 'status_display',
            'gateway_response', 'is_test', 'created_at', 'processed_at'
        ]
        read_only_fields = [
            'transaction_id', 'created_at', 'processed_at'
        ]