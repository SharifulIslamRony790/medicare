from django.db import models
from django.conf import settings

# ==============================================================================
# FEATURE: PATIENT PROFILE
# PURPOSE: Stores patient demographics, medical history, and contact information.
# ==============================================================================
class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    allergies = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    medical_history = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='patients/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_patients')

    def save(self, *args, **kwargs):
        if not self.image:
            from medicare_core.utils import generate_profile_image
            img_content = generate_profile_image(self.name)
            if img_content:
                self.image.save(f"{self.name}_profile.png", img_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
