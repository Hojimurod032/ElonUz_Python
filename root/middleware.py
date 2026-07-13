from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UpdateLastOnlineMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            now = timezone.now()

            if not request.user.last_online or (now - request.user.last_online).total_seconds() > 300:
                request.user.last_online = now
                request.user.save(update_fields=['last_online'])