
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Count, Prefetch
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer, MpesaPaymentSerializer
from .filters import PaymentFilter
from .pagination import OptimizedPagination
from .mpesa_utils import initiate_stk_push
from decouple import config

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

class MpesaPaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MpesaPaymentSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            order_id = serializer.validated_data['order_id']

            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            amount = int(order.total)

            # Create a payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total,
                currency=order.currency,
                method=Payment.PaymentMethod.MPESA,
                phone_number=phone_number,
                status=Payment.PaymentStatus.PENDING,
            )

            # Initiate STK push
            shortcode = config('MPESA_SHORTCODE')
            passkey = config('MPESA_PASSKEY')
            callback_url = config('CALLBACK_URL')

            response_data = initiate_stk_push(
                phone_number,
                amount,
                str(order.id),
                shortcode,
                passkey,
                callback_url
            )

            if response_data and response_data.get('ResponseCode') == '0':
                payment.mpesa_request_id = response_data['CheckoutRequestID']
                payment.save()
                return Response({
                    "message": "STK push initiated successfully.",
                    "CheckoutRequestID": response_data['CheckoutRequestID']
                }, status=status.HTTP_200_OK)
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.gateway_response = response_data
                payment.save()
                return Response({
                    "error": "Failed to initiate STK push.",
                    "details": response_data
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MpesaCallbackView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

        if not checkout_request_id:
            return Response({"error": "Invalid callback data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(mpesa_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')

        payment.gateway_response = data

        if result_code == 0:
            payment.status = Payment.PaymentStatus.PAID
            payment.order.payment_status = Order.PaymentStatus.PAID

            # Extract transaction ID
            metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
            for item in metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.transaction_id = item.get('Value')
                    break
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.order.payment_status = Order.PaymentStatus.FAILED

        payment.save()
        payment.order.save()

        return Response(status=status.HTTP_200_OK)