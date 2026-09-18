from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from .forms import AppointmentForm, PatientAppointmentForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Provides secure REST API endpoints for Appointment data.
# ==============================================================================
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Prevent API Information Disclosure (IDOR)
        if self.request.user.role == 'patient':
            if hasattr(self.request.user, 'patient_profile'):
                return Appointment.objects.filter(patient=self.request.user.patient_profile)
            return Appointment.objects.none()
            
        elif self.request.user.role == 'doctor':
            if hasattr(self.request.user, 'doctor_profile'):
                return Appointment.objects.filter(doctor=self.request.user.doctor_profile)
            return Appointment.objects.none()
            
        # Admin or staff can see all
        return Appointment.objects.all()

    def perform_update(self, serializer):
        # Patients can only cancel their appointments via API
        if self.request.user.role == 'patient':
            if serializer.validated_data.get('status') not in [None, 'cancelled']:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Patients can only cancel appointments.")
        serializer.save()

from django.http import JsonResponse
from datetime import datetime, timedelta

# ==============================================================================
# FEATURE: DYNAMIC SCHEDULING
# PURPOSE: Calculates available 10-minute slots for a doctor on a specific date,
#          taking into account their work schedule, existing appointments, and leaves.
# ==============================================================================
@login_required
def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    from doctors.models import DoctorLeave, DoctorSchedule
    # 1. Check for leave
    if DoctorLeave.objects.filter(doctor_id=doctor_id, date=date_obj).exists():
        return JsonResponse({'slots': [], 'message': 'Doctor is on leave this day.'})

    day_name = date_obj.strftime('%A')
    
    # 2. Get schedule
    schedule = DoctorSchedule.objects.filter(doctor_id=doctor_id, day_of_week=day_name).first()
    if not schedule:
        return JsonResponse({'slots': [], 'message': 'Doctor does not sit on this day.'})

    # 3. Generate all possible 10-minute slots
    slots = []
    current_time = datetime.combine(date_obj, schedule.start_time)
    end_time = datetime.combine(date_obj, schedule.end_time)
    
    while current_time < end_time:
        slots.append(current_time.time())
        current_time += timedelta(minutes=10)

    # 4. Remove booked slots
    booked_appointments = Appointment.objects.filter(
        doctor_id=doctor_id, date=date_obj
    ).exclude(status='cancelled')
    booked_time_strs = [appt.time.strftime('%H:%M') for appt in booked_appointments]

    available_slots = [t.strftime('%H:%M') for t in slots if t.strftime('%H:%M') not in booked_time_strs]

    return JsonResponse({'slots': available_slots, 'message': 'success'})

# ==============================================================================
# FEATURE: UI VIEWS (List, Complete, Cancel, Add)
# PURPOSE: Handles web interface actions for managing appointments based on role.
# ==============================================================================
@login_required
def appointment_list(request):
    # Filter to show only logged-in user's appointments
    if request.user.role == 'patient':
        if hasattr(request.user, 'patient_profile'):
            appointments = Appointment.objects.filter(patient=request.user.patient_profile).select_related('doctor', 'patient').order_by('-date', '-time')
        else:
            appointments = Appointment.objects.none()
    elif request.user.role == 'doctor':
        # Doctors see appointments booked with them
        if hasattr(request.user, 'doctor_profile'):
            appointments = Appointment.objects.filter(doctor=request.user.doctor_profile).select_related('doctor', 'patient').order_by('-date', '-time')
        else:
            appointments = Appointment.objects.none()
    else:
        # Admin/staff can see all appointments
        appointments = Appointment.objects.all().select_related('doctor', 'patient').order_by('-date', '-time')
    return render(request, 'appointment_list.html', {'appointments': appointments})

@login_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    # Only the assigned doctor or admin/staff can complete the appointment
    if request.user.role == 'doctor':
        if hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile:
            appointment.status = 'completed'
            appointment.save()
            return redirect('appointment_list')
    else:
        # Admin/superuser can also complete
        if request.user.is_superuser or request.user.role in ['admin', 'staff']:
            appointment.status = 'completed'
            appointment.save()
            return redirect('appointment_list')
            
    return redirect('appointment_list')

@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    is_patient_owner = False
    if request.user.role == 'patient' and hasattr(request.user, 'patient_profile'):
        is_patient_owner = (appointment.patient == request.user.patient_profile)
            
    is_doctor_owner = False
    if request.user.role == 'doctor' and hasattr(request.user, 'doctor_profile'):
        is_doctor_owner = (appointment.doctor == request.user.doctor_profile)
            
    is_admin_or_receptionist = request.user.is_superuser or request.user.can_register_patients()
    
    if is_patient_owner or is_doctor_owner or is_admin_or_receptionist:
        if appointment.status in ['pending', 'confirmed']:
            appointment.status = 'cancelled'
            appointment.save()
            
    return redirect('appointment_list')

@login_required
def appointment_add(request):
    # Patients book for themselves, doctors/admin/staff can book for any patient
    is_patient = request.user.role == 'patient'
    can_book_for_others = request.user.is_superuser or request.user.role == 'doctor' or request.user.can_register_patients()
    
    if not (is_patient or can_book_for_others):
        return render(request, 'error_403.html', {'message': "You don't have permission to book appointments."})
        
    if request.method == 'POST':
        form = PatientAppointmentForm(request.POST) if is_patient else AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Enforce Patient Identity to prevent IDOR
            if is_patient:
                appointment.patient = request.user.patient_profile
                
            appointment.created_by = request.user
            
            try:
                # Force clean to run custom model validations (double booking, doctor availability)
                appointment.full_clean()
                appointment.save()
                
                # Send Email Notification TO User asynchronously
                if appointment.status == 'confirmed' and appointment.patient.email:
                    subject = 'Appointment Confirmed - MediCare'
                    message = f"""
                    Dear {appointment.patient.name},

                    Your appointment has been confirmed.

                    Doctor: {appointment.doctor.name}
                    Date: {appointment.date}
                    Time: {appointment.time}

                    Thank you for choosing MediCare.
                    """
                    import threading
                    
                    def send_async_email(subject, message, recipient_list):
                        try:
                            send_mail(
                                subject,
                                message,
                                settings.EMAIL_HOST_USER,
                                recipient_list,
                                fail_silently=True,
                            )
                        except Exception as e:
                            print(f"Error sending email: {e}")
                            
                    email_thread = threading.Thread(
                        target=send_async_email,
                        args=(subject, message, [appointment.patient.email])
                    )
                    email_thread.start()

                return redirect('appointment_list')
            except ValidationError as e:
                # Add validation errors to form to show user
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field != '__all__' else None, error)
                else:
                    for error in e.messages:
                        form.add_error(None, error)
    else:
        initial_data = {}
        doctor_id = request.GET.get('doctor')
        if doctor_id:
            initial_data['doctor'] = doctor_id
        form = PatientAppointmentForm(initial=initial_data) if is_patient else AppointmentForm(initial=initial_data)
    
    return render(request, 'appointment_form.html', {'form': form})
