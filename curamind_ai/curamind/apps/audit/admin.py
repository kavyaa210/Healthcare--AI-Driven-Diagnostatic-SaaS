from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ['timestamp', 'user', 'action', 'ip_address']
    list_filter     = ['action']
    readonly_fields = ['user', 'action', 'description', 'ip_address', 'timestamp', 'resource']
    def has_add_permission(self, request):    return False
    def has_change_permission(self, request, obj=None): return False
