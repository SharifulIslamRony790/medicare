from django import forms
from django.forms import inlineformset_factory
from .models import Prescription, Medication

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['appointment', 'symptoms', 'diagnosis', 'advice']
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['medicine_name', 'dosage', 'duration', 'instruction']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Napa Extend'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1-0-1'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7 Days'}),
            'instruction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'After meal'}),
        }

MedicationFormSet = inlineformset_factory(
    Prescription, 
    Medication, 
    form=MedicationForm,
    extra=1, 
    can_delete=True
)
