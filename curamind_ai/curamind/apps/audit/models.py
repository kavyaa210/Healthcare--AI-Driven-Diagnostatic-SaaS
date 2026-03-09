from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditLog(models.Model):
    ACTION_TYPES = [
        ('REGISTER_INITIATED',       'Registration'),
        ('LOGIN_SUCCESS',            'Login'),
        ('LOGIN_FAILED',             'Login Failed'),
        ('LOGOUT',                   'Logout'),
        ('PASSWORD_RESET_REQUESTED', 'Password Reset'),
        ('EMR_VIEWED',               'EMR Viewed'),
        ('EMR_CREATED',              'EMR Created'),
        ('APPT_CREATED',             'Appointment Created'),
        ('UNAUTHORIZED_ACCESS',      'Unauthorized Access'),
    ]

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='audit_logs')
    action      = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(default=timezone.now)
    resource    = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        u = self.user.email if self.user else 'Anonymous'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {u} — {self.action}"
