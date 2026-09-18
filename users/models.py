from django.contrib.auth.models import AbstractUser
from django.db import models

# ==============================================================================
# FEATURE: CUSTOM USER MODEL
# PURPOSE: Extends Django's default AbstractUser to include role-based access 
#          control (RBAC) and role-specific permission helper methods.
# ==============================================================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('staff', 'Staff'),
        ('patient', 'Patient'), 
    )
    # The primary role defining the user's capabilities in the system
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    # --------------------------------------------------------------------------
    # PERMISSION HELPER METHODS
    # Purpose: Determine what features this user can access across the platform.
    # --------------------------------------------------------------------------
    def can_register_patients(self):
        """Checks if the user can create and manage patient accounts."""
        if self.is_superuser or self.role == 'admin':
            return True
        if self.role == 'staff' and hasattr(self, 'staff_profile'):
            return self.staff_profile.sub_role in ['receptionist']
        return False

    def can_manage_billing(self):
        """Checks if the user can create invoices and process payments."""
        if self.is_superuser or self.role == 'admin':
            return True
        if self.role == 'staff' and hasattr(self, 'staff_profile'):
            return self.staff_profile.sub_role in ['cashier', 'manager']
        return False

    def can_access_clinical_data(self):
        """Checks if the user can access patient clinical records/prescriptions."""
        if self.is_superuser or self.role == 'admin' or self.role == 'doctor':
            return True
        if self.role == 'staff' and hasattr(self, 'staff_profile'):
            return self.staff_profile.sub_role in ['nurse', 'pharmacist', 'manager']
        return False

    def can_handle_support(self):
        """Checks if the user can handle customer support operations."""
        if self.is_superuser or self.role == 'admin':
            return True
        if self.role == 'staff' and hasattr(self, 'staff_profile'):
            return self.staff_profile.sub_role in ['support_agent', 'manager', 'receptionist']
        return False

    def __str__(self):
        return f"{self.username} ({self.role})"
