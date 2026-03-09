from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_at', 'status', 'is_teleconsult')
    list_filter = ('status', 'is_teleconsult', 'created_at')
    search_fields = ('patient__user__email', 'doctor__user__email')
    readonly_fields = ('created_at', 'updated_at')

