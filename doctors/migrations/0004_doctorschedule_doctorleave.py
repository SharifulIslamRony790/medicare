from django.db import migrations, models
import django.db.models.deletion
import datetime

def populate_schedules(apps, schema_editor):
    Doctor = apps.get_model('doctors', 'Doctor')
    DoctorSchedule = apps.get_model('doctors', 'DoctorSchedule')
    
    # Map of prefixes to full day names to cleanly migrate old data
    day_map = {
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday'
    }
    
    for doctor in Doctor.objects.all():
        if getattr(doctor, 'available_days', None):
            # Parse the string like "Monday, Wed, Friday"
            days = [d.strip() for d in doctor.available_days.split(',') if d.strip()]
            for day in days:
                full_day = None
                for prefix, full in day_map.items():
                    if day.lower().startswith(prefix.lower()):
                        full_day = full
                        break
                
                if full_day:
                    DoctorSchedule.objects.get_or_create(
                        doctor=doctor,
                        day_of_week=full_day,
                        defaults={
                            'start_time': datetime.time(9, 0),
                            'end_time': datetime.time(15, 0)
                        }
                    )


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0003_doctor_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=15)),
                ('start_time', models.TimeField(default='09:00:00')),
                ('end_time', models.TimeField(default='15:00:00')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='doctors.doctor')),
            ],
            options={
                'unique_together': {('doctor', 'day_of_week')},
            },
        ),
        migrations.CreateModel(
            name='DoctorLeave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='doctors.doctor')),
            ],
            options={
                'unique_together': {('doctor', 'date')},
            },
        ),
        migrations.RunPython(populate_schedules, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='doctor',
            name='available_days',
        ),
    ]
