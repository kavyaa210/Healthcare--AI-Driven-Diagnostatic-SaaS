from django.contrib import admin
from .custom_admin import curamind_admin_site as admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',        admin.urls),
    path('accounts/',     include('apps.accounts.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('',              include('apps.accounts.dashboard_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
