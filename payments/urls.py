from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('mpesa-payment/', views.MpesaPaymentView.as_view(), name='mpesa-payment'),
    path('mpesa-callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
]