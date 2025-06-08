from django.contrib.auth.views import LogoutView

class LogoutViewAllowGet(LogoutView):
    """Allow logout via GET requests for convenience."""

    def get(self, request, *args, **kwargs):
        """Redirect GET requests to POST to avoid CSRF issues with stale pages."""
        return self.post(request, *args, **kwargs)
