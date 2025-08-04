from django.urls import path
from .views import (
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserLogoutAllAPIView,
    UserProfileAPIView,
    UserAPIView,
    EmailVerificationAPIView,
    ResendVerificationEmailAPIView
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('logout-all/', UserLogoutAllAPIView.as_view(), name='logout-all'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    path('me/', UserAPIView.as_view(), name='user-detail'),
    path('verify-email/<str:uidb64>/<str:token>/',
         EmailVerificationAPIView.as_view(),
         name='verify-email'),
    path('resend-verification-email/',
         ResendVerificationEmailAPIView.as_view(), 
         name='resend-verification-email'),
]