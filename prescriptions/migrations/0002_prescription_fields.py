from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('prescriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='diagnosis',
            field=models.TextField(blank=True, help_text="Doctor's diagnosis", null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='symptoms',
            field=models.TextField(blank=True, help_text='Patient symptoms', null=True),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='medicines',
            field=models.TextField(blank=True, help_text='Legacy: List of medicines with dosage', null=True),
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=200)),
                ('dosage', models.CharField(help_text='e.g., 1-0-1, 1+1+1', max_length=50)),
                ('duration', models.CharField(help_text='e.g., 7 Days, 1 Month', max_length=50)),
                ('instruction', models.CharField(blank=True, help_text='e.g., After meal, before sleep', max_length=200, null=True)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='prescriptions.prescription')),
            ],
        ),
    ]
