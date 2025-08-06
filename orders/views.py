from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Count
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
import logging

from payments.models import Payment
from payments.mpesa_utils import initiate_stk_push
from decouple import config
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

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        logging.info("Checkout process started.")
        try:
            cart = Cart.objects.get(user=request.user)
            logging.info(f"Cart {cart.id} found for user {request.user.id}.")
        except Cart.DoesNotExist:
            logging.error(f"Cart not found for user {request.user.id}.")
            return Response(
                {'error': _('Cart not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if cart.is_empty:
            return Response(
                {'error': _('Cannot checkout with an empty cart')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logging.error(f"Serializer errors: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                logging.info("Creating order...")
                # Create order
                try:
                    order = Order.objects.create(
                        user=request.user,
                        status=Order.OrderStatus.PENDING,
                        payment_status=Order.PaymentStatus.PENDING,
                        customer_notes=serializer.validated_data.get('customer_notes', ''),
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    logging.info(f"Order {order.id} created.")
                    try:
                        logging.info(f"Order {order.id} created successfully with number {order.number}")
                    except Exception as e:
                        logging.error(f"Error creating order: {str(e)}")
                        raise

                except IntegrityError:
                    logging.error("Failed to create order due to an integrity error. Retrying...")
                    order = Order.objects.create(
                        user=request.user,
                        status=Order.OrderStatus.PENDING,
                        payment_status=Order.PaymentStatus.PENDING,
                        customer_notes=serializer.validated_data.get('customer_notes', ''),
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    logging.info(f"Order {order.id} created on retry.")
                
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
                logging.info("Cart cleared.")

                logging.info("Recalculating order totals...")
                # Recalculate order totals
                order.calculate_totals()
                order.save()
                logging.info("Order totals recalculated.")

                logging.info("Creating payment...")
                # Create payment
                payment_method = serializer.validated_data['payment_method']
                phone_number = serializer.validated_data.get('mpesa_phone_number')

                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    currency=order.currency,
                    method=payment_method,
                    phone_number=phone_number,
                    status=Payment.PaymentStatus.PENDING,
                )
                logging.info(f"Payment {payment.id} created.")

                if payment_method == Order.PaymentMethod.MPESA:
                    logging.info("Initiating M-Pesa payment...")
                    # Initiate STK push
                    shortcode = config('MPESA_SHORTCODE')
                    passkey = config('MPESA_PASSKEY')
                    callback_url = config('CALLBACK_URL')

                    response_data = initiate_stk_push(
                        phone_number,
                        int(order.total),
                        str(order.id),
                        shortcode,
                        passkey,
                        callback_url
                    )

                    if response_data and response_data.get('ResponseCode') == '0':
                        payment.mpesa_request_id = response_data['CheckoutRequestID']
                        payment.save()
                        logging.info("M-Pesa payment initiated successfully.")
                    else:
                        payment.status = Payment.PaymentStatus.FAILED
                        payment.gateway_response = response_data
                        payment.save()
                        order.payment_status = Order.PaymentStatus.FAILED
                        order.save()
                        logging.error(f"Failed to initiate M-Pesa payment: {response_data}")
                        return Response({
                            "error": "Failed to initiate M-Pesa payment.",
                            "details": response_data
                        }, status=status.HTTP_400_BAD_REQUEST)

                logging.info("Checkout process completed successfully.")

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