# middleware.py

from django.utils import timezone
from django.conf import settings

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Reset the session expiry time
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        
        response = self.get_response(request)
        return response
