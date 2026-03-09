from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CuraMindUser, DoctorProfile, PatientProfile, SystemStatus


@admin.register(CuraMindUser)
class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(DoctorProfile)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'hospital', 'available']
    list_filter  = ['available', 'specialization']


@admin.register(PatientProfile)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group', 'assigned_doctor', 'emergency_contact']

    def patient_name(self, obj):
        return obj.user.get_full_name()
    patient_name.short_description = 'Patient'


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ['is_online', 'maintenance_mode']

    def has_add_permission(self, request):
        # prevent the creation of multiple rows
        return not SystemStatus.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
