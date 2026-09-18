from django.db import migrations, models

def update_legacy_roles(apps, schema_editor):
    User = apps.get_model('users', 'User')
    # All users who registered normally via signup form previously got role='staff' 
    # but were not actually staff or superusers. Fix them to 'patient'.
    User.objects.filter(role='staff', is_staff=False, is_superuser=False).update(role='patient')

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('doctor', 'Doctor'), ('staff', 'Staff'), ('patient', 'Patient')], default='patient', max_length=10),
        ),
        migrations.RunPython(update_legacy_roles, reverse_code=migrations.RunPython.noop),
    ]
