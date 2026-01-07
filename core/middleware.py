
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.http import JsonResponse
from django.core.cache import cache
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            raw_token = auth_header.split(' ')[1]

            try:
                # Validate the token
                token = AccessToken(raw_token)

                # Get the JTI (unique identifier) from the token
                jti = token['jti']

                # Check cache for blacklisted token
                if cache.get(f"blacklisted_{jti}"):
                    return JsonResponse({'error': 'Token is blacklisted'}, status=401)

                # Query the database if not in cache
                if BlacklistedToken.objects.filter(token__jti=jti).exists():
                    cache.set(f"blacklisted_{jti}", True, timeout=3600)  # Cache for 1 hour
                    return JsonResponse({'error': 'Token is blacklisted'}, status=401)

            except (InvalidToken, TokenError) as e:
                logger.error(f"Invalid token: {e}")
                return JsonResponse({'error': 'Invalid token'}, status=401)
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
                return JsonResponse({'error': 'An error occurred while processing the token'}, status=500)

        # Proceed with the request if no issues
        response = self.get_response(request)
        return response

# -----------------------------------------------------------------
# No index middleware
class NoIndexMiddleware:
    """
    Adds an X-Robots-Tag header to all responses to prevent indexing
    when running in non-production environments.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if we're not in production before setting the header
        if getattr(settings, 'DJANGO_ENV', 'development') != 'production':
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response