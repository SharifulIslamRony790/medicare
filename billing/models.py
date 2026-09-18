from django.db import models
from patients.models import Patient
from appointments.models import Appointment
from django.conf import settings

# ==============================================================================
# FEATURE: INVOICE MODEL
# PURPOSE: Manages patient billing, tracking amounts, statuses, and approval.
# ==============================================================================
class Invoice(models.Model):
    STATUS_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    items = models.TextField(blank=True, null=True, help_text="Legacy: Description of billed items")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False) # Legacy flag
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_invoices')
    
    # Approval fields
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_invoices')
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_invoice = Invoice.objects.get(pk=self.pk)
            if old_invoice.status == 'Paid' and getattr(self, '_bypass_immutability', False) == False:
                from django.core.exceptions import ValidationError
                raise ValidationError("Paid invoices are immutable and cannot be modified.")
                
        if self.status == 'Paid':
            self.is_paid = True
        else:
            self.is_paid = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient.name}"

# ==============================================================================
# FEATURE: INVOICE ITEM
# PURPOSE: Represents individual line items (services, medicines) within an invoice.
# ==============================================================================
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - ${self.amount}"

# ==============================================================================
# FEATURE: PAYMENT MODEL
# PURPOSE: Tracks successful payments, transaction IDs, and methods for invoices.
# ==============================================================================
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('VISA', 'Visa Card'),
        ('MASTERCARD', 'MasterCard'),
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('CASH', 'Cash'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} Payment - {self.transaction_id}"
