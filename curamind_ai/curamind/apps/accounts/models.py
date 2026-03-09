from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class Role(models.TextChoices):
    PATIENT = 'PATIENT', 'Patient'
    DOCTOR  = 'DOCTOR',  'Doctor'
    NURSE   = 'NURSE',   'Nurse'
    ADMIN   = 'ADMIN',   'Admin'


class CuraMindUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role',         Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class CuraMindUser(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=15, blank=True)
    role        = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CuraMindUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'CuraMind User'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_patient(self): return self.role == Role.PATIENT
    def is_doctor(self):  return self.role == Role.DOCTOR
    def is_nurse(self):   return self.role == Role.NURSE
    def is_admin(self):   return self.role == Role.ADMIN


class DoctorProfile(models.Model):
    user           = models.OneToOneField(CuraMindUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    hospital       = models.CharField(max_length=200, blank=True)
    experience_yrs = models.IntegerField(default=0)
    available      = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} — {self.specialization}"


class PatientProfile(models.Model):
    BLOOD_GROUPS = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                    ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]

    user              = models.OneToOneField(CuraMindUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth     = models.DateField(null=True, blank=True)
    blood_group       = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    address           = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    allergies         = models.TextField(blank=True)
    assigned_doctor   = models.ForeignKey(
        DoctorProfile, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='patients'
    )

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class SystemStatus(models.Model):
    """Singleton model representing the global system state.

    - **is_online**: whether the platform is accepting non-admin traffic.
    - **maintenance_mode**: additional flag when the system is under maintenance.

    Only one row is ever created; `get_solo` returns that single instance.
    """

    is_online = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # always enforce a single row with PK=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        if not self.is_online:
            return "Offline"
        if self.maintenance_mode:
            return "Maintenance"
        return "Online"
