from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
from .models import CuraMindUser, Role, DoctorProfile, PatientProfile, SystemStatus
from apps.audit.utils import log_action


def get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0] if x else request.META.get('REMOTE_ADDR')


# ── REGISTER
class RegisterView(View):
    def get(self, request):
        # block registration if system is down or in maintenance
        status = SystemStatus.get_solo()
        if (not status.is_online) or status.maintenance_mode:
            messages.error(request, 'Registration is not available while the system is offline or undergoing maintenance.')
            return redirect('login')
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/register.html', {'system_status': status})

    def post(self, request):
        status = SystemStatus.get_solo()
        if (not status.is_online) or status.maintenance_mode:
            messages.error(request, 'Registration is not available while the system is offline or undergoing maintenance.')
            return redirect('login')

        email      = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        role       = request.POST.get('role', Role.PATIENT)
        password   = request.POST.get('password', '')
        confirm_pw = request.POST.get('confirm_password', '')

        if not all([email, first_name, last_name, password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html', {'system_status': status})

        if password != confirm_pw:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'system_status': status})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/register.html', {'system_status': status})

        if CuraMindUser.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html', {'system_status': status})

        # create user with elevated flags for admin role
        user = CuraMindUser.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            phone=phone, role=role,
        )

        if role == Role.ADMIN:
            # make sure they can access Django admin and have all perms
            user.is_staff = True
            user.is_superuser = True
            user.save()

        if role == Role.PATIENT:
            PatientProfile.objects.create(user=user)
        elif role == Role.DOCTOR:
            DoctorProfile.objects.create(
                user=user,
                license_number=request.POST.get('license_number', f'LIC{user.id:06d}'),
                specialization=request.POST.get('specialization', 'General Physician'),
            )

        log_action(user, 'REGISTER_INITIATED', f'New {role} registered: {email}', get_ip(request))
        login(request, user)
        messages.success(request, f'Welcome to CuraMind AI, {first_name}! 🎉')
        return redirect('dashboard')


# ── LOGIN
class LoginView(View):
    def get(self, request):
        # always show login page (admin may need to log in even if system is down)
        if request.user.is_authenticated:
            return redirect('dashboard')
        context = {'system_status': SystemStatus.get_solo()}
        return render(request, 'accounts/login.html', context)

    def post(self, request):
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        ip       = get_ip(request)

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, 'Invalid email or password.')
            log_action(None, 'LOGIN_FAILED', f'Failed login: {email}', ip)
            return render(request, 'accounts/login.html', {'system_status': SystemStatus.get_solo()})

        # when the platform is offline/maintenance we only allow admins to authenticate
        status = SystemStatus.get_solo()
        if (not status.is_online or status.maintenance_mode) and not user.is_admin():
            messages.error(request, 'The system is currently offline or in maintenance mode. Please try again later.')
            log_action(user, 'LOGIN_BLOCKED', f'Login blocked by maintenance/offline status: {email}', ip)
            return render(request, 'accounts/login.html', {'system_status': status})

        login(request, user)
        log_action(user, 'LOGIN_SUCCESS', f'User logged in: {email}', ip)
        messages.success(request, f'Welcome back, {user.first_name}! 👋')
        return redirect('dashboard')


# ── PASSWORD RESET REQUEST
class PasswordResetRequestView(View):
    def get(self, request):
        return render(request, 'accounts/password_reset.html')

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        try:
            user = CuraMindUser.objects.get(email=email)
            # In production: send reset email here
            messages.success(request, f'Password reset instructions sent to {email}.')
            log_action(user, 'PASSWORD_RESET_REQUESTED', f'Reset requested: {email}', get_ip(request))
        except CuraMindUser.DoesNotExist:
            messages.info(request, f'If {email} exists, a reset email has been sent.')
        return redirect('login')


# ── LOGOUT
def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, 'LOGOUT', 'User logged out', get_ip(request))
    logout(request)
    messages.success(request, 'You have been logged out securely.')
    return redirect('login')


# ── DASHBOARD
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # always grab latest system status for dashboards
    status = SystemStatus.get_solo()

    from apps.emr.models import MedicalRecord, Appointment as EMRAppointment
    from apps.appointments.models import Appointment as BookedAppointment

    user = request.user
    context = {'user': user}

    if user.is_patient():
        # Get both EMR appointments and booked appointments
        emr_appointments = EMRAppointment.objects.filter(patient=user).order_by('-scheduled_at')[:5]
        booked_appointments = BookedAppointment.objects.filter(patient=user.patient_profile).order_by('-scheduled_at')[:5]
        
        # Combine and sort
        all_appointments = list(emr_appointments) + list(booked_appointments)
        all_appointments.sort(key=lambda x: x.scheduled_at, reverse=True)
        context['appointments'] = all_appointments[:5]
        context['records']      = MedicalRecord.objects.filter(patient=user).order_by('-created_at')[:5]

    elif user.is_doctor():
        # Get both EMR appointments and booked appointments for this doctor
        emr_appointments = EMRAppointment.objects.filter(doctor__user=user).order_by('-scheduled_at')[:10]
        booked_appointments = BookedAppointment.objects.filter(doctor__user=user).order_by('-scheduled_at')[:10]
        
        # Combine and sort
        all_appointments = list(emr_appointments) + list(booked_appointments)
        all_appointments.sort(key=lambda x: x.scheduled_at, reverse=True)
        context['appointments'] = all_appointments[:10]
        
        # Count unique patients from both sources
        emr_patients = set(EMRAppointment.objects.filter(doctor__user=user).values_list('patient_id', flat=True))
        booked_patients = set(BookedAppointment.objects.filter(doctor__user=user).values_list('patient__user_id', flat=True))
        context['patient_count'] = len(emr_patients | booked_patients)
    elif user.is_admin():
        # Custom admin dashboard stats
        context['user_count'] = CuraMindUser.objects.count()
        context['appointment_count'] = BookedAppointment.objects.count() + EMRAppointment.objects.count()
        context['records_count'] = MedicalRecord.objects.count()
        context['system_status'] = status
        # maybe additional info later

    return render(request, 'dashboard/home.html', context)


# ── ADMIN PANEL (FRONTEND)


def system_unavailable_view(request):
    """Display a simple maintenance/offline message to non-admins."""
    status = SystemStatus.get_solo()
    return render(request, 'accounts/system_unavailable.html', {'status': status})

def admin_panel_view(request):
    """Simple admin-only page. Only users with role ADMIN should see this."""
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('dashboard')
    
    # allow toggling online/offline/maintenance
    status = SystemStatus.get_solo()
    if request.method == 'POST':
        # toggle values; use presence of checkbox names since unchecked boxes
        # aren't submitted
        status.is_online = bool(request.POST.get('is_online'))
        status.maintenance_mode = bool(request.POST.get('maintenance_mode'))
        status.save()
        from django.contrib import messages as _msgs
        _msgs.success(request, 'System status updated successfully.')

    # gather some global stats
    from apps.emr.models import MedicalRecord, Appointment as EMRAppointment
    from apps.appointments.models import Appointment as BookedAppointment
    
    context = {
        'user_count': CuraMindUser.objects.count(),
        'appointment_count': BookedAppointment.objects.count() + EMRAppointment.objects.count(),
        'records_count': MedicalRecord.objects.count(),
        'system_status': status,
    }
    return render(request, 'accounts/admin_panel.html', context)
