from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer
from .forms import PatientSignupForm, PatientProfileCompletionForm, DoctorSignupForm, DoctorProfileCompletionForm, CustomAuthenticationForm

User = get_user_model()
BACKEND = 'django.contrib.auth.backends.ModelBackend'

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Handles REST API endpoints for User data management.
# ==============================================================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ==============================================================================
# FEATURE: AUTHENTICATION
# PURPOSE: Handles user login and session management across all roles.
# ==============================================================================
def login_view(request):
    """Unified login view for all roles (Patient, Doctor, Staff)"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # Fallback to email login
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
                    
            if user is not None:
                login(request, user, backend=BACKEND)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

# ==============================================================================
# FEATURE: USER REGISTRATION (SIGNUP)
# PURPOSE: Handles the signup processes for different user roles (Patient, Doctor).
# ==============================================================================
def signup_view(request):
    """Redirect to patient signup portal by default."""
    return redirect('patient_signup')

def patient_signup_view(request):
    """Dedicated patient signup view"""
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()
            
            # Patient profile is auto-created via signals in users/signals.py
            
            login(request, user, backend=BACKEND)
            
            # Send Professional Welcome Email
            if user.email:
                import threading
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = 'Welcome to MediCare - Your Health, Our Priority!'
                
                html_message = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                        <div style="max-width: 600px; margin: 20px auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                            <div style="background-color: #2563eb; color: #ffffff; padding: 20px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px;">Welcome to MediCare!</h1>
                            </div>
                            <div style="padding: 30px; background-color: #ffffff;">
                                <p style="font-size: 16px; color: #1f2937;">Dear <strong>{user.username}</strong>,</p>
                                <p style="font-size: 16px; color: #4b5563;">Thank you for signing up with MediCare! We are thrilled to have you on board.</p>
                                <p style="font-size: 16px; color: #4b5563;">Please complete your profile to book appointments and easily manage your healthcare services with us.</p>
                                <br>
                                <p style="font-size: 16px; color: #4b5563; margin-bottom: 5px;">Stay Healthy,</p>
                                <p style="font-size: 16px; color: #1f2937; margin-top: 0;"><strong>The MediCare Team</strong></p>
                            </div>
                        </div>
                    </body>
                </html>
                """
                
                plain_message = f"Dear {user.username},\n\nWelcome to MediCare! We are thrilled to have you on board.\n\nPlease complete your profile to book appointments and easily manage your healthcare services with us.\n\nStay Healthy,\nThe MediCare Team"
                
                def send_welcome_email(sub, txt_msg, html_msg, recipient):
                    try:
                        send_mail(
                            sub,
                            txt_msg,
                            settings.EMAIL_HOST_USER,
                            [recipient],
                            fail_silently=True,
                            html_message=html_msg
                        )
                    except Exception as e:
                        print(f"Error sending welcome email: {e}")
                        
                email_thread = threading.Thread(
                    target=send_welcome_email,
                    args=(subject, plain_message, html_message, user.email)
                )
                email_thread.start()

            messages.success(request, 'Account created successfully! Please complete your profile.')
            return redirect('complete_profile')
    else:
        form = PatientSignupForm()
    return render(request, 'patient_signup.html', {'form': form})

# ==============================================================================
# FEATURE: PROFILE COMPLETION
# PURPOSE: Handles the onboarding process for users to complete their profiles
#          after initial registration.
# ==============================================================================
@login_required
def complete_profile_view(request):
    """Onboarding step to complete patient profile"""
    try:
        patient = request.user.patient_profile
    except:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = PatientProfileCompletionForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile completed successfully! Welcome to MediCare.')
            return redirect('home')
    else:
        form = PatientProfileCompletionForm(instance=patient)
    return render(request, 'complete_profile.html', {'form': form})

def doctor_signup_view(request):
    """Dedicated doctor signup view"""
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'doctor'
            user.save()
            
            # Update the auto-created doctor profile with the real name
            if hasattr(user, 'doctor_profile'):
                user.doctor_profile.name = form.cleaned_data.get('name')
                user.doctor_profile.save()
            
            # The signal automatically creates the base Doctor object
            login(request, user, backend=BACKEND)
            messages.success(request, 'Account created successfully! Please complete your professional profile.')
            return redirect('complete_doctor_profile')
    else:
        form = DoctorSignupForm()
    return render(request, 'doctor_signup.html', {'form': form})

@login_required
def complete_doctor_profile_view(request):
    """Onboarding step to complete doctor profile"""
    try:
        doctor = request.user.doctor_profile
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = DoctorProfileCompletionForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            
            # Handle available days
            days_str = form.cleaned_data.get('available_days', '')
            days = [d.strip() for d in days_str.split(',') if d.strip()]
            if days:
                from doctors.models import DoctorSchedule
                # Clear existing default schedules
                doctor.schedules.all().delete()
                for day in days:
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        day_of_week=day.capitalize(),
                        start_time='09:00:00',
                        end_time='15:00:00'
                    )
                    
            messages.success(request, 'Professional Profile completed successfully! Welcome to MediCare.')
            return redirect('home')
    else:
        # Pre-fill available_days if schedules exist
        days = doctor.schedules.values_list('day_of_week', flat=True)
        initial_days = ", ".join(days) if days else "Monday"
        form = DoctorProfileCompletionForm(instance=doctor, initial={'available_days': initial_days})
        
    return render(request, 'complete_doctor_profile.html', {'form': form})

# ==============================================================================
# FEATURE: LOGOUT
# PURPOSE: Ends the user session and redirects to login.
# ==============================================================================
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

# ==============================================================================
# FEATURE: ACCOUNT SETTINGS
# PURPOSE: Allows users to update their credentials and role-specific profiles.
# ==============================================================================
@login_required
def settings_view(request):
    doctor_form = None
    if request.user.role == 'doctor' and hasattr(request.user, 'doctor_profile'):
        doctor = request.user.doctor_profile
        if request.method == 'POST' and 'update_doctor_profile' in request.POST:
            doctor_form = DoctorProfileCompletionForm(request.POST, request.FILES, instance=doctor)
            if doctor_form.is_valid():
                doctor_form.save()
                
                # Handle available days
                days_str = doctor_form.cleaned_data.get('available_days', '')
                days = [d.strip() for d in days_str.split(',') if d.strip()]
                if days:
                    from doctors.models import DoctorSchedule
                    doctor.schedules.all().delete()
                    for day in days:
                        DoctorSchedule.objects.create(
                            doctor=doctor,
                            day_of_week=day.capitalize(),
                            start_time='09:00:00',
                            end_time='15:00:00'
                        )
                messages.success(request, 'Professional Profile updated successfully.')
                return redirect('settings')
        else:
            days = doctor.schedules.values_list('day_of_week', flat=True)
            initial_days = ", ".join(days) if days else "Monday"
            doctor_form = DoctorProfileCompletionForm(instance=doctor, initial={'available_days': initial_days})

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user = request.user
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Account settings updated successfully.')
            return redirect('settings')
        
        elif 'change_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct the error below.')
    
    # Initialize password form if not POST or not change_password POST
    if request.method != 'POST' or 'change_password' not in request.POST:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'settings.html', {'password_form': form, 'doctor_form': doctor_form})
