from django import forms
from .models import Doctor, DoctorLeave

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['user', 'name', 'phone', 'specialty', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DoctorLeaveForm(forms.ModelForm):
    class Meta:
        model = DoctorLeave
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional reason'})
        }
