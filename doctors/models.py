from django.db import models
from django.conf import settings

# ==============================================================================
# FEATURE: DOCTOR PROFILE
# PURPOSE: Stores professional details and links to the core User model.
# ==============================================================================
class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    specialty = models.CharField(max_length=100)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.image:
            from medicare_core.utils import generate_profile_image
            img_content = generate_profile_image(self.name)
            if img_content:
                self.image.save(f"{self.name}_profile.png", img_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.specialty}"

# ==============================================================================
# FEATURE: DOCTOR SCHEDULE
# PURPOSE: Manages the weekly availability (days and hours) for each doctor.
# ==============================================================================
class DoctorSchedule(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES)
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='15:00:00')
    
    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week} ({self.start_time} to {self.end_time})"

# ==============================================================================
# FEATURE: DOCTOR LEAVE
# PURPOSE: Records specific dates when a doctor is unavailable for appointments.
# ==============================================================================
class DoctorLeave(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leaves')
    date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('doctor', 'date')

    def __str__(self):
        return f"{self.doctor.name} on Leave: {self.date}"
