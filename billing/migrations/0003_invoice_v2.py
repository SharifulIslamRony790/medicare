from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='amount',
            new_name='total_amount',
        ),
        migrations.AddField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('Unpaid', 'Unpaid'), ('Partial', 'Partial'), ('Paid', 'Paid')], default='Unpaid', max_length=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='items',
            field=models.TextField(blank=True, help_text='Legacy: Description of billed items', null=True),
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='billing.invoice')),
            ],
        ),
    ]
