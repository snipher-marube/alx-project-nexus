from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
import logging
from users.utils.tokens import email_verification_token_generator

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ProfileSerializer,
    AuthUserSerializer
)
from .models import User

logger = logging.getLogger(__name__)

class ResendVerificationThrottle(AnonRateThrottle):
    scope = 'resend_verification'

class UserRegistrationAPIView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "user": AuthUserSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
            "message": "User created successfully. Please verify your email."
        }, status=status.HTTP_201_CREATED)


class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        return Response({
            "user": AuthUserSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
            "message": "Login successful"
        })


class UserLogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request._auth.delete()
        return Response({
            "message": "Successfully logged out"
        }, status=status.HTTP_200_OK)


class UserLogoutAllAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token_set.all().delete()
        return Response({
            "message": "Successfully logged out from all devices"
        }, status=status.HTTP_200_OK)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Handle profile picture deletion if null is passed
        if 'profile_picture' in self.request.data and not self.request.data['profile_picture']:
            instance.profile_picture.delete(save=True)


class UserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    



class EmailVerificationAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            logger.info(f"Verification request for user {uidb64}")
            
            from users.utils.email import EmailVerification
            user = EmailVerification.verify_token(uidb64, token)
            
            return Response(
                {
                    "detail": "Email successfully verified",
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            logger.error(f"Verification failed: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.critical(f"Unexpected verification error: {str(e)}", exc_info=True)
            return Response(
                {"detail": "An error occurred during verification"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResendVerificationEmailAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request):
        user = request.user
        if user.is_verified:
            return Response(
                {"detail": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from users.utils.email import EmailVerification
        EmailVerification.send_verification_email(user, request)
        
        return Response(
            {"detail": "Verification email sent successfully"},
            status=status.HTTP_200_OK
        )