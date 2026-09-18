from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    """Form for Admins, Staff, and Doctors who can book for anyone"""
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '600'}), # 10 min increments
        }

class PatientAppointmentForm(forms.ModelForm):
    """Form strictly for Patients to book for themselves"""
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '600'}), # 10 min increments
        }
