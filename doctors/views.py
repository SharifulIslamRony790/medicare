from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Doctor
from .serializers import DoctorSerializer
from .forms import DoctorForm

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Provides secure REST API endpoints for Doctor data.
# ==============================================================================
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

# ==============================================================================
# FEATURE: DOCTOR LIST & DETAIL (UI)
# PURPOSE: Handles searching, listing, and viewing individual doctor profiles.
# ==============================================================================
def doctor_list(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.select_related('user').all()
    if query:
        from django.db.models import Q
        doctors = doctors.filter(Q(name__icontains=query) | Q(specialty__icontains=query))
    return render(request, 'doctor_list.html', {'doctors': doctors, 'query': query})

def doctor_detail(request, pk):
    from django.shortcuts import get_object_or_404
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, 'doctor_detail.html', {'doctor': doctor})

# ==============================================================================
# FEATURE: DOCTOR MANAGEMENT
# PURPOSE: Allows admins/staff to add new doctors to the system.
# ==============================================================================
@login_required
def doctor_add(request):
    # Only admin/superuser/staff can add doctors
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff']):
        return HttpResponseForbidden("You don't have permission to access this page.")
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'doctor_form.html', {'form': form})

# ==============================================================================
# FEATURE: DOCTOR LEAVE MANAGEMENT
# PURPOSE: Allows doctors to declare, view, and cancel leaves/days off.
# ==============================================================================
@login_required
def doctor_leave_list(request):
    if not hasattr(request.user, 'doctor_profile'):
        return HttpResponseForbidden("Only doctors can access this page.")
        
    from .models import DoctorLeave
    leaves = DoctorLeave.objects.filter(doctor=request.user.doctor_profile).order_by('-date')
    return render(request, 'doctor_leave_list.html', {'leaves': leaves})

@login_required
def doctor_leave_add(request):
    if not hasattr(request.user, 'doctor_profile'):
        return HttpResponseForbidden("Only doctors can access this page.")
        
    from .forms import DoctorLeaveForm
    if request.method == 'POST':
        form = DoctorLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = request.user.doctor_profile
            # Check if an appointment exists on this day? For simplicity, we just save it.
            # In production, we'd warn the doctor.
            leave.save()
            return redirect('doctor_leave_list')
    else:
        form = DoctorLeaveForm()
        
    return render(request, 'doctor_leave_form.html', {'form': form})

@login_required
def doctor_leave_delete(request, pk):
    if not hasattr(request.user, 'doctor_profile'):
        return HttpResponseForbidden("Only doctors can access this page.")
        
    from .models import DoctorLeave
    from django.shortcuts import get_object_or_404
    leave = get_object_or_404(DoctorLeave, pk=pk, doctor=request.user.doctor_profile)
    leave.delete()
    return redirect('doctor_leave_list')

# ==============================================================================
# FEATURE: DOCTOR DASHBOARD
# PURPOSE: Personalized dashboard for doctors showing their upcoming appointments
#          and daily statistics.
# ==============================================================================
@login_required
def doctor_dashboard_view(request):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
        
    doctor = request.user.doctor_profile
    
    from django.utils import timezone
    today = timezone.now().date()
    
    # Appointments
    today_appointments = doctor.appointments.filter(date=today).order_by('time')
    upcoming_appointments = doctor.appointments.filter(date__gt=today).order_by('date', 'time')[:5]
    
    # Stats
    total_patients = doctor.appointments.values('patient').distinct().count()
    pending_appointments = doctor.appointments.filter(status='pending').count()
    completed_appointments = doctor.appointments.filter(status='completed').count()

    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_patients': total_patients,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'doctor_dashboard.html', context)
