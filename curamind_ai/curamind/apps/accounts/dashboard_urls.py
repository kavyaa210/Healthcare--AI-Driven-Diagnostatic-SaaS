from django.urls import path
from .views import dashboard_view, admin_panel_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('',           dashboard_view, name='home'),
    path('admin-panel/', admin_panel_view, name='admin_panel'),
]
