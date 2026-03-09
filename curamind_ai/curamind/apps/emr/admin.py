from django.contrib import admin
from .models import MedicalRecord, MedicalImage, Appointment


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display  = ['title', 'patient', 'doctor', 'record_type', 'created_at']
    list_filter   = ['record_type']
    search_fields = ['title', 'patient__email']


@admin.register(MedicalImage)
class MedicalImageAdmin(admin.ModelAdmin):
    list_display = ['medical_record', 'image_type', 'uploaded_at', 'uploaded_by']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'doctor', 'scheduled_at', 'status', 'is_teleconsult']
    list_filter   = ['status', 'is_teleconsult']
    search_fields = ['patient__email']
