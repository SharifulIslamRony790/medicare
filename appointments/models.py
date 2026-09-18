from django.db import models
from patients.models import Patient
from doctors.models import Doctor
from django.conf import settings

# ==============================================================================
# FEATURE: APPOINTMENT MODEL
# PURPOSE: Manages the scheduling, status, and validation of doctor appointments.
# ==============================================================================
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointments')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'],
                condition=~models.Q(status='cancelled'),
                name='unique_active_appointment'
            )
        ]

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        
        # Skip validations if cancelling or completing
        if self.status in ['cancelled', 'completed']:
            return
            
        # 1. Prevent double booking
        if self.doctor and self.date and self.time:
            existing = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time=self.time
            ).exclude(status='cancelled')
            
            if self.pk:
                existing = existing.exclude(pk=self.pk)
                
            if existing.exists():
                raise ValidationError("This doctor is already booked for this specific date and time.")

        # 2. Check Doctor Availability (Schedule and Leaves)
        if self.doctor and self.date and self.time:
            from doctors.models import DoctorLeave, DoctorSchedule
            
            # Check for leaves
            if DoctorLeave.objects.filter(doctor=self.doctor, date=self.date).exists():
                raise ValidationError(f"Doctor {self.doctor.name} is on leave on {self.date}.")
            
            day_name_full = self.date.strftime('%A')
            
            # Check schedule
            schedule = DoctorSchedule.objects.filter(doctor=self.doctor, day_of_week=day_name_full).first()
            if not schedule:
                raise ValidationError(f"Doctor {self.doctor.name} does not take appointments on {day_name_full}s.")
            
            # Check time falls within schedule
            if not (schedule.start_time <= self.time <= schedule.end_time):
                raise ValidationError(f"On {day_name_full}s, Doctor {self.doctor.name} is only available between {schedule.start_time.strftime('%I:%M %p')} and {schedule.end_time.strftime('%I:%M %p')}.")

        # 3. Check Time Validity (10-min intervals)
        if self.time:
            if self.time.minute % 10 != 0 or self.time.second != 0:
                raise ValidationError("Appointments are scheduled in 10-minute intervals (e.g., 09:00, 09:10, 09:20).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        time_str = self.time.strftime('%I:%M %p') if self.time else ''
        return f"{self.patient.name} | {self.date} at {time_str}"
