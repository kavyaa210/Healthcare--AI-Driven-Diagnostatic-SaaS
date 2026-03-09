from django.contrib.admin import AdminSite, site as default_admin_site


class CuraMindAdminSite(AdminSite):
    site_header = 'CuraMind Administration'
    site_title = 'CuraMind Admin'
    index_title = 'Site Administration'

    def has_permission(self, request):
        user = request.user
        # Only allow users with role ADMIN and active
        return bool(user.is_active and hasattr(user, 'role') and user.role == 'ADMIN')


# instantiate single site
curamind_admin_site = CuraMindAdminSite()

# override the default admin site used by django.contrib.admin
import django.contrib.admin as _dj_admin
_dj_admin.site = curamind_admin_site

