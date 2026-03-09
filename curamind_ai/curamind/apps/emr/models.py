from django.db import models
from django.conf import settings
from django.utils import timezone
import os


def medical_image_path(instance, filename):
    ext  = filename.split('.')[-1].lower()
    name = f"img_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('medical_images', str(instance.medical_record.patient.id), name)


class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('CONSULTATION', 'Consultation Notes'),
        ('LAB_RESULT',   'Lab Results'),
        ('PRESCRIPTION', 'Prescription'),
        ('RADIOLOGY',    'Radiology Report'),
        ('DISCHARGE',    'Discharge Summary'),
        ('VACCINATION',  'Vaccination Record'),
    ]
    patient     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='medical_records', limit_choices_to={'role': 'PATIENT'})
    doctor      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='created_records', limit_choices_to={'role': 'DOCTOR'})
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='CONSULTATION')
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    diagnosis   = models.TextField(blank=True)
    prescription= models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.patient.get_full_name()}"


class MedicalImage(models.Model):
    IMAGE_TYPES = [('DICOM','DICOM'),('XRAY','X-Ray'),('MRI','MRI'),('CT','CT Scan'),('OTHER','Other')]
    medical_record     = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='images')
    image_file         = models.FileField(upload_to=medical_image_path)
    image_type         = models.CharField(max_length=10, choices=IMAGE_TYPES, default='OTHER')
    description        = models.CharField(max_length=300, blank=True)
    ai_analysis_result = models.TextField(blank=True)
    uploaded_at        = models.DateTimeField(auto_now_add=True)
    uploaded_by        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                           null=True, related_name='uploaded_images')

    def __str__(self):
        return f"{self.image_type} — {self.medical_record.patient.get_full_name()}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'), ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('NO_SHOW', 'No Show'),
    ]
    patient        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='patient_appointments', limit_choices_to={'role': 'PATIENT'})
    doctor         = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE,
                                       related_name='appointments')
    scheduled_at   = models.DateTimeField()
    duration_min   = models.IntegerField(default=30)
    reason         = models.TextField()
    status         = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    notes          = models.TextField(blank=True)
    is_teleconsult = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.patient.get_full_name()} → Dr.{self.doctor.user.get_full_name()} @ {self.scheduled_at.strftime('%d %b %Y')}"
