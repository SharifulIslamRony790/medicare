from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from prescriptions.models import Prescription

def home(request):
    # Redirect unauthenticated users to patient login portal
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {}
    
    if request.user.role == 'patient':
        try:
            profile = request.user.patient_profile
            from billing.models import Invoice
            context['invoice_count'] = Invoice.objects.filter(patient=profile).count()
            context['doctor_count'] = Doctor.objects.count()
            context['appointment_count'] = Appointment.objects.filter(patient=profile).count()
            context['prescription_count'] = Prescription.objects.filter(appointment__patient=profile).count()
        except:
            context['invoice_count'] = 0
            context['doctor_count'] = 0
            context['appointment_count'] = 0
            context['prescription_count'] = 0
            
    elif request.user.role == 'doctor':
        try:
            profile = request.user.doctor_profile
            context['patient_count'] = Patient.objects.filter(appointments__doctor=profile).distinct().count()
            context['doctor_count'] = Doctor.objects.count()
            context['appointment_count'] = Appointment.objects.filter(doctor=profile).count()
            context['prescription_count'] = Prescription.objects.filter(appointment__doctor=profile).count()
        except:
            context['patient_count'] = 0
            context['doctor_count'] = 0
            context['appointment_count'] = 0
            context['prescription_count'] = 0
            
    else: # admin, staff
        context['patient_count'] = Patient.objects.count()
        context['doctor_count'] = Doctor.objects.count()
        context['appointment_count'] = Appointment.objects.count()
        context['prescription_count'] = Prescription.objects.count()

    return render(request, 'home.html', context)

from django.contrib import messages
from dashboard.models import ContactMessage
import urllib.request
import urllib.parse
import json
from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def contact(request):
    if request.method == 'POST':
        # 1. Rate Limiting Check
        ip = get_client_ip(request)
        cache_key = f'contact_rate_{ip}'
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 5:
            messages.error(request, "You are sending too many messages. Please try again after 1 minute.")
            return redirect('contact')
            
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        recaptcha_response = request.POST.get('g-recaptcha-response')
        
        # 2. reCAPTCHA Verification
        if not recaptcha_response:
            messages.error(request, "Please check the 'I\\'m not a robot' box.")
            return redirect('contact')
            
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        if not result.get('success'):
            messages.error(request, "Invalid reCAPTCHA. Please try again.")
            return redirect('contact')
        
        # 3. Save Message
        if name and email and message:
            # Increment rate limit counter
            cache.set(cache_key, request_count + 1, 60)
            
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, f"Thank you {name}! Your message has been sent successfully. Our support team will get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill out all the fields.")
            
    return render(request, 'contact.html')

def support(request):
    return render(request, 'support.html')

def privacy(request):
    return render(request, 'privacy.html')

def user_guide(request):
    return render(request, 'user_guide.html')

def faqs(request):
    return render(request, 'faqs.html')

def live_chat(request):
    return render(request, 'live_chat.html')
