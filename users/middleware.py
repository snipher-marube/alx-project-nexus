from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

class AccountVerificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip for these paths
        if request.path in [
            '/api/v1/auth/register/',
            '/api/v1/auth/login/',
            '/api/v1/auth/verify-email/',
            '/api/v1/auth/resend-verification-email/',
            '/api/v1/auth/logout/',
            '/api/v1/auth/password/reset/',
        ]:
            return None

        if request.user.is_authenticated and not request.user.is_verified:
            return JsonResponse(
                {
                    'detail': 'Please verify your email address to access this resource.',
                    'code': 'email_not_verified'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return None