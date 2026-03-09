from django.db import models
from apps.accounts.models import PatientProfile, DoctorProfile
from django.conf import settings
from django.utils import timezone


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient        = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appt_bookings')
    doctor         = models.ForeignKey(DoctorProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='appt_bookings')
    scheduled_at   = models.DateTimeField()
    is_teleconsult = models.BooleanField(default=False)
    notes          = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(default=timezone.now)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"Appointment: {self.patient.user.get_full_name()} - {self.scheduled_at}"


class AppointmentAttachment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='attachments')
    file        = models.FileField(upload_to='attachments/%Y/%m/%d')
    label       = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='uploaded_attachments'
    )
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Attachment for {self.appointment} - {self.file.name}"

    def filename(self):
        """Returns just the filename without the full path"""
        import os
        return os.path.basename(self.file.name)

    def is_image(self):
        """Returns True if the file is an image (for preview in templates)"""
        name = self.file.name.lower()
        return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    def is_pdf(self):
        """Returns True if the file is a PDF"""
        return self.file.name.lower().endswith('.pdf')


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor      = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    text        = models.TextField()
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription by {self.doctor.user.get_full_name()} on {self.created_at:%Y-%m-%d}"