from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from patients.models import Patient

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_patient_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Patient profile for newly registered users
    if their role is 'patient' or if they signed up via a social provider 
    (where role might not be explicitly set during the auth flow).
    """
    # Prevent signal execution during loaddata (raw=True) to avoid duplicate key errors
    if kwargs.get('raw'):
        return

    if created:
        # If no role is set or it's implicitly a patient (or via google), 
        # ensure they have a Patient profile so the dashboard doesn't crash.
        # Note: If it's explicitly a doctor/admin created elsewhere, 
        # they usually have the role set beforehand.
        
        # If it's a doctor/admin, skip (unless you want them to also be patients)
        if instance.role in ['admin', 'doctor', 'staff'] and getattr(instance, '_bypass_patient_creation', False):
            return

        # Ensure role is set to patient if it's missing
        if not instance.role:
            instance.role = 'patient'
            instance.save(update_fields=['role'])

        if instance.role == 'patient':
            Patient.objects.get_or_create(
                user=instance,
                defaults={
                    'name': instance.get_full_name() or instance.username,
                    'email': instance.email
                }
            )
            
        elif instance.role == 'doctor':
            from doctors.models import Doctor, DoctorSchedule
            doctor, created_doc = Doctor.objects.get_or_create(
                user=instance,
                defaults={
                    'name': instance.get_full_name() or instance.username,
                    'phone': 'N/A',
                    'specialty': 'General Physician'
                }
            )
            if created_doc:
                DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    day_of_week='Monday',
                    defaults={'start_time': '09:00:00', 'end_time': '15:00:00'}
                )
