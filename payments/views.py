
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Count, Prefetch
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter
from .pagination import OptimizedPagination

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('order')
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['amount', 'created_at', 'processed_at']
    ordering = ['-created_at']
    pagination_class = OptimizedPagination
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by order number if provided
        order_number = self.request.query_params.get('order')
        if order_number:
            queryset = queryset.filter(order__number=order_number)
        
        return queryset