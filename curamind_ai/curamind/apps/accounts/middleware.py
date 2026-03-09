from django.shortcuts import redirect
from django.urls import reverse

from .models import SystemStatus


class SystemStatusMiddleware:
    """Middleware that prevents non-admin users from accessing the system when it's offline
    or in maintenance mode.

    Admin users may still reach the login page so they can authenticate.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        status = SystemStatus.get_solo()
        # if everything is normal, nothing special to do
        if status.is_online and not status.maintenance_mode:
            return self.get_response(request)

        user = request.user
        # allow the admin site login unconditionally (superusers will be admins)
        admin_login_url = reverse('admin:login')
        allowed = {
            reverse('login'),
            reverse('password_reset'),
            reverse('register'),
            reverse('system_unavailable'),
            admin_login_url,
        }

        # if user is authenticated and is an admin, bypass restrictions
        if user.is_authenticated and getattr(user, 'is_admin', lambda: False)():
            return self.get_response(request)

        # if the requested path is in the allowlist, let it through so that
        # a non-admin user can still see the login page (they will be blocked
        # during authentication) or see the unavailable message.
        if request.path in allowed:
            return self.get_response(request)

        # otherwise redirect to the maintenance/offline notice
        return redirect('system_unavailable')
