from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PatientSignupForm(UserCreationForm):
    # Minimal initial fields
    name = forms.CharField(max_length=100, required=True, label="Full Name")

    class Meta:
        model = User
        fields = ('username', 'email', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

class PatientProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['age', 'gender', 'phone', 'address', 'medical_history', 'image']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'gender' and not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'

class DoctorSignupForm(UserCreationForm):
    # Minimal initial fields
    name = forms.CharField(max_length=100, required=True, label="Full Name")

    class Meta:
        model = User
        fields = ('username', 'email', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

class DoctorProfileCompletionForm(forms.ModelForm):
    available_days = forms.CharField(
        max_length=200, 
        required=True, 
        help_text="Comma-separated days, e.g., Monday, Wednesday"
    )

    class Meta:
        from doctors.models import Doctor
        model = Doctor
        fields = ['specialty', 'phone', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
