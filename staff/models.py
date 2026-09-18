from django.db import models
from django.conf import settings

# ==============================================================================
# FEATURE: STAFF PROFILE
# PURPOSE: Stores details and specific sub-roles (e.g., Nurse, Cashier, Receptionist) 
#          for hospital staff, enabling granular RBAC across the application.
# ==============================================================================
class Staff(models.Model):
    STAFF_ROLE_CHOICES = (
        ('receptionist', 'Receptionist'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('cashier', 'Cashier'),
        ('manager', 'Manager'),
        ('support_agent', 'Support Agent'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    name = models.CharField(max_length=100)
    sub_role = models.CharField(max_length=20, choices=STAFF_ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='staff/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.image:
            from medicare_core.utils import generate_profile_image
            img_content = generate_profile_image(self.name)
            if img_content:
                self.image.save(f"{self.name}_profile.png", img_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_sub_role_display()}"
