from django.db import models
from appointments.models import Appointment

# ==============================================================================
# FEATURE: PRESCRIPTION MODEL
# PURPOSE: Stores clinical diagnosis, symptoms, and advice given by a doctor 
#          during a specific appointment.
# ==============================================================================
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    symptoms = models.TextField(blank=True, null=True, help_text="Patient symptoms")
    diagnosis = models.TextField(blank=True, null=True, help_text="Doctor's diagnosis")
    medicines = models.TextField(blank=True, null=True, help_text="Legacy: List of medicines with dosage")
    advice = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment}"

# ==============================================================================
# FEATURE: MEDICATION MODEL
# PURPOSE: Represents individual drugs/medicines prescribed in a Prescription,
#          including dosage, duration, and specific instructions.
# ==============================================================================
class Medication(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=50, help_text="e.g., 1-0-1, 1+1+1")
    duration = models.CharField(max_length=50, help_text="e.g., 7 Days, 1 Month")
    instruction = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., After meal, before sleep")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
