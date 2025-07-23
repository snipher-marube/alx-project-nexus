from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Count
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import (
    Order, OrderItem, ShippingAddress, BillingAddress,
    Cart, CartItem
)
from .serializers import (
    OrderSerializer,
    OrderStatusHistorySerializer,
    CartSerializer, CartItemSerializer, CheckoutSerializer
)
from .filters import OrderFilter
from .pagination import OptimizedPagination



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'user', 'shipping_address', 'billing_address'
    ).prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related(
            'product', 'variant', 'variant__product'
        )),
        'status_history'
    ).annotate(
        item_count=Count('items')
    )
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = [
        'number', 'user__email', 'user__first_name', 'user__last_name',
        'shipping_address__first_name', 'shipping_address__last_name',
        'shipping_address__email', 'shipping_address__phone'
    ]
    ordering_fields = [
        'number', 'status', 'payment_status', 'total',
        'created_at', 'updated_at', 'paid_at'
    ]
    ordering = ['-created_at']
    pagination_class = OptimizedPagination
    lookup_field = 'number'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own orders
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset

    @action(detail=True, methods=['post'])
    def cancel(self, request, number=None):
        order = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            order.cancel(reason=reason)
            return Response(
                {'status': 'Order cancelled successfully'},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def status_history(self, request, number=None):
        order = self.get_object()
        history = order.status_history.select_related('created_by')
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related(
        Prefetch('items', queryset=CartItem.objects.select_related(
            'product', 'variant', 'variant__product'
        ))
    )
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptimizedPagination

    def get_object(self):
        # Get or create cart for the current user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        
        if cart.is_empty:
            return Response(
                {'error': _('Cannot checkout with an empty cart')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create order
                order_data = {
                    'user': request.user,
                    'status': Order.OrderStatus.PENDING,
                    'payment_status': Order.PaymentStatus.PENDING,
                    'payment_method': serializer.validated_data['payment_method'],
                    'customer_notes': serializer.validated_data.get('customer_notes', ''),
                    'ip_address': request.META.get('REMOTE_ADDR')
                }
                order_serializer = OrderSerializer(
                    data=order_data,
                    context={'request': request}
                )
                order_serializer.is_valid(raise_exception=True)
                order = order_serializer.save()
                
                # Create order items from cart items
                for cart_item in cart.items.all():
                    item_data = {
                        'order': order,
                        'product': cart_item.product,
                        'variant': cart_item.variant,
                        'quantity': cart_item.quantity,
                        'price': cart_item.price
                    }
                    OrderItem.objects.create(**item_data)
                
                # Create addresses
                shipping_address_data = serializer.validated_data['shipping_address']
                ShippingAddress.objects.create(
                    order=order,
                    **shipping_address_data
                )
                
                if serializer.validated_data['use_shipping_as_billing']:
                    BillingAddress.objects.create(
                        order=order,
                        **shipping_address_data
                    )
                elif 'billing_address' in serializer.validated_data:
                    BillingAddress.objects.create(
                        order=order,
                        **serializer.validated_data['billing_address']
                    )
                
                # Clear the cart
                cart.items.all().delete()
                
                # Recalculate order totals
                order.calculate_totals()
                order.save()
                
                return Response(
                    OrderSerializer(order, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.select_related('product', 'variant', 'variant__product')

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def perform_update(self, serializer):
        instance = serializer.instance
        new_quantity = serializer.validated_data.get('quantity', instance.quantity)
        
        if instance.variant:
            if new_quantity > instance.variant.quantity and instance.variant.track_quantity:
                raise ValidationError(
                    _("Requested quantity exceeds available inventory")
                )
        elif instance.product:
            if new_quantity > instance.product.quantity and instance.product.track_quantity:
                raise ValidationError(
                    _("Requested quantity exceeds available inventory")
                )
        
        serializer.save()