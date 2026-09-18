from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer
from .forms import PatientForm

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Provides secure REST API endpoints for Patient data.
# ==============================================================================
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

# ==============================================================================
# FEATURE: PATIENT MANAGEMENT (Staff & Doctors)
# PURPOSE: Handles listing and adding new patients by authorized staff.
# ==============================================================================
@login_required
def patient_list(request):
    # Admin/superuser, staff, and doctors can see patient list
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']):
        return render(request, 'error_403.html', {'message': "You don't have permission to access this page."})
    if request.user.role == 'doctor' and hasattr(request.user, 'doctor_profile'):
        # Doctors only see patients who have booked an appointment with them
        patients = Patient.objects.filter(appointments__doctor=request.user.doctor_profile).distinct().select_related('user').order_by('-created_at')
    else:
        # Admin and staff see all patients
        patients = Patient.objects.select_related('user').all().order_by('-created_at')
        
    return render(request, 'patient_list.html', {'patients': patients})

@login_required
def patient_add(request):
    # Check if user has permission to add patients
    if not request.user.can_register_patients():
        return render(request, 'error_403.html', {'message': "You don't have permission to add patients."})
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form})

# ==============================================================================
# FEATURE: PATIENT PROFILE & DASHBOARD
# PURPOSE: Handles viewing individual profiles and the personalized dashboard 
#          for patients, including profile updates and deactivation.
# ==============================================================================
@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    # Users can only see their own patient profile, admin/superuser/staff/doctors can see all
    if hasattr(request.user, 'patient_profile'):
        if patient != request.user.patient_profile and not (request.user.is_superuser or request.user.role in ['admin', 'staff', 'doctor']):
            return HttpResponseForbidden("You don't have permission to access this page.")
    return render(request, 'patient_detail.html', {'patient': patient})

@login_required
def patient_dashboard_view(request):
    try:
        patient = request.user.patient_profile
    except:
        from django.contrib import messages
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        if 'deactivate' in request.POST:
            request.user.is_active = False
            request.user.save()
            from django.contrib.auth import logout
            logout(request)
            from django.contrib import messages
            messages.success(request, 'Your account has been deactivated.')
            return redirect('home')
        
        from users.forms import PatientProfileCompletionForm
        form = PatientProfileCompletionForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_dashboard')
    else:
        from users.forms import PatientProfileCompletionForm
        form = PatientProfileCompletionForm(instance=patient)

    appointments = patient.appointments.all().order_by('-date')[:5]
    
    return render(request, 'patient_dashboard.html', {
        'patient': patient,
        'form': form,
        'appointments': appointments
    })
