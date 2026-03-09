from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Appointment
from .models import Appointment, Prescription, AppointmentAttachment
from django.urls import reverse
from django.shortcuts import HttpResponseRedirect


@login_required
def book_appointment(request):
    """View for booking a new appointment"""
    from apps.accounts.models import DoctorProfile

    if request.method == 'POST':
        # Handle form submission
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes', '')
        doctor_id = request.POST.get('doctor')
        
        # Combine date and time into datetime
        scheduled_at = datetime.combine(
            datetime.strptime(appointment_date, '%Y-%m-%d').date(),
            datetime.strptime(appointment_time, '%H:%M').time()
        )
        
        doctor = DoctorProfile.objects.filter(pk=doctor_id).first() if doctor_id else None
        
        # Get patient profile
        patient = request.user.patient_profile
        
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduled_at=scheduled_at,
            notes=notes,
            status='pending'
        )
        
        return redirect('appointments:appointment_detail', pk=appointment.pk)
    
    # GET: show form with available doctors
    doctors = DoctorProfile.objects.filter(available=True)
    return render(request, 'appointments/book_appointment.html', {'doctors': doctors})


@login_required
def appointment_list(request):
    """View for listing appointments"""
    # Show patient appointments to patients, and assigned appointments to doctors
    appointments = Appointment.objects.none()
    if hasattr(request.user, 'patient_profile'):
        appointments = Appointment.objects.filter(patient=request.user.patient_profile)
    elif hasattr(request.user, 'doctor_profile'):
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile)
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments
    })


@login_required
def appointment_detail(request, pk):
    """View for appointment detail"""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Permission: allow the patient who booked it, the assigned doctor, or staff
    user = request.user
    is_allowed = False
    if hasattr(user, 'patient_profile') and appointment.patient == user.patient_profile:
        is_allowed = True
    if hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile:
        is_allowed = True
    if user.is_staff or user.is_superuser:
        is_allowed = True

    if not is_allowed:
        return HttpResponseForbidden('You do not have permission to view this appointment.')

    # Handle doctor creating a prescription
    if request.method == 'POST' and 'prescription' in request.POST:
        if not hasattr(request.user, 'doctor_profile') or appointment.doctor != request.user.doctor_profile:
            return HttpResponseForbidden('Only the assigned doctor can add a prescription.')
        text = request.POST.get('prescription', '').strip()
        if text:
            Prescription.objects.create(appointment=appointment, doctor=request.user.doctor_profile, text=text)
        return HttpResponseRedirect(reverse('appointments:appointment_detail', args=[appointment.pk]))

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'attachments': appointment.attachments.all(),
        'prescriptions': appointment.prescriptions.all(),
    })
