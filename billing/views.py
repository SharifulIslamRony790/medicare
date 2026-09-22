from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Invoice, Payment
from .serializers import InvoiceSerializer
from .forms import InvoiceForm, InvoiceItemFormSet
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

from django.core.mail import send_mail
from django.conf import settings

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Provides REST endpoints for Invoices.
# ==============================================================================
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

# ==============================================================================
# FEATURE: INVOICE MANAGEMENT (List, Create, Detail, Approve)
# PURPOSE: Handles creating invoices by staff, viewing them by patients, 
#          and the approval workflow for managers.
# ==============================================================================
@login_required
def invoice_list(request):
    # Filter to show only logged-in user's invoices
    if hasattr(request.user, 'patient_profile') and request.user.role == 'patient':
        invoices = Invoice.objects.filter(patient=request.user.patient_profile, is_approved=True).select_related('patient', 'appointment').order_by('-date')
    elif request.user.can_manage_billing():
        # Admin, Cashier, Manager can see all invoices
        invoices = Invoice.objects.all().select_related('patient', 'appointment').order_by('-date')
    else:
        return render(request, 'error_403.html', {'message': "You don't have permission to view invoices."})
    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
def invoice_add(request):
    # Only admin/superuser or cashier can create invoices
    has_permission = False
    if request.user.is_superuser or request.user.role == 'admin':
        has_permission = True
    elif request.user.role == 'staff' and hasattr(request.user, 'staff_profile'):
        if request.user.staff_profile.sub_role == 'cashier':
            has_permission = True
            
    if not has_permission:
        return render(request, 'error_403.html', {'message': "You don't have permission to create invoices. Only Cashiers and Admins can create bills."})
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.is_approved = False # Force manual approval workflow
            invoice.save()
            formset.instance = invoice
            formset.save()
            
            # Calculate total_amount
            total = sum(item.amount for item in invoice.line_items.all())
            invoice.total_amount = total
            invoice.save()
            
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
        
    from prescriptions.models import Prescription
    import json
    prescriptions = Prescription.objects.all().values_list('appointment_id', 'id')
    prescription_map = {str(app_id): rx_id for app_id, rx_id in prescriptions if app_id}
    
    context = {
        'form': form, 
        'formset': formset,
        'prescription_map_json': json.dumps(prescription_map)
    }
    return render(request, 'invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check permissions
    has_permission = False
    if hasattr(request.user, 'patient_profile') and invoice.patient == request.user.patient_profile:
        if invoice.is_approved:
            has_permission = True
    elif request.user.can_manage_billing():
        has_permission = True
        
    if not has_permission:
        return render(request, 'error_403.html', {'message': "You don't have permission to view this invoice."})
        
    return render(request, 'invoice_detail.html', {'invoice': invoice})

# ==============================================================================
# FEATURE: PAYMENT PROCESSING
# PURPOSE: Handles the selection of payment methods, processing mock transactions,
#          and asynchronously sending email receipts to patients.
# ==============================================================================
@login_required
def payment_select(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can pay, and it must be approved
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return render(request, 'error_403.html', {'message': "You can only pay your own invoices."})
        if not invoice.is_approved:
            return render(request, 'error_403.html', {'message': "This invoice is pending approval and cannot be paid yet."})
    else:
        return render(request, 'error_403.html', {'message': "Only patients can pay invoices."})
    
    if invoice.is_paid:
        return redirect('invoice_detail', pk=invoice_id)
    return render(request, 'payment_select.html', {'invoice': invoice})

@login_required
def payment_process(request, invoice_id, method):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can pay, and it must be approved
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return render(request, 'error_403.html', {'message': "You can only pay your own invoices."})
        if not invoice.is_approved:
            return render(request, 'error_403.html', {'message': "This invoice is pending approval and cannot be paid yet."})
    else:
        return render(request, 'error_403.html', {'message': "Only patients can pay invoices."})
    
    if request.method == 'POST':
        # Simulate payment processing
        transaction_id = str(uuid.uuid4())
        payment_obj = Payment.objects.create(
            invoice=invoice,
            method=method.upper(),
            transaction_id=transaction_id,
            amount=invoice.total_amount
        )
        invoice.status = 'Paid'
        invoice.save()

        # Send Email Notification TO User asynchronously
        patient_user = invoice.patient.user
        if patient_user and patient_user.email:
            subject = 'Payment Receipt - MediCare'
            
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 0;">
                    <div style="max-width: 600px; margin: 20px auto; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                        <div style="background-color: #3b82f6; color: #ffffff; padding: 20px; text-align: center;">
                            <h1 style="margin: 0; font-size: 24px;">Payment Received!</h1>
                        </div>
                        <div style="padding: 30px; background-color: #ffffff;">
                            <p style="font-size: 16px; color: #1f2937;">Dear <strong>{patient_user.username}</strong>,</p>
                            <p style="font-size: 16px; color: #4b5563;">Thank you for your payment. Your transaction was successful.</p>
                            
                            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                                <p style="margin: 5px 0;"><strong>Invoice ID:</strong> #{invoice.id}</p>
                                <p style="margin: 5px 0;"><strong>Amount Paid:</strong> ${invoice.total_amount}</p>
                                <p style="margin: 5px 0;"><strong>Transaction ID:</strong> {transaction_id}</p>
                                <p style="margin: 5px 0;"><strong>Method:</strong> {method.upper()}</p>
                            </div>
                            
                            <p style="font-size: 16px; color: #4b5563;">We have attached a PDF copy of your receipt to this email for your records.</p>
                            <br>
                            <p style="font-size: 16px; color: #4b5563; margin-bottom: 5px;">Stay Healthy,</p>
                            <p style="font-size: 16px; color: #1f2937; margin-top: 0;"><strong>The MediCare Team</strong></p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            plain_message = f"Dear {patient_user.username},\n\nThank you for your payment. Your transaction was successful.\n\nInvoice ID: #{invoice.id}\nAmount Paid: ${invoice.total_amount}\nTransaction ID: {transaction_id}\nMethod: {method.upper()}\n\nWe have attached a PDF copy of your receipt to this email for your records.\n\nStay Healthy,\nThe MediCare Team"
            
            pdf_bytes = generate_receipt_pdf_bytes(payment_obj)
            
            import threading
            from django.core.mail import EmailMultiAlternatives
            
            def send_async_receipt(subject, txt_msg, html_msg, recipient_list, pdf_data, p_id):
                try:
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=txt_msg,
                        from_email=settings.EMAIL_HOST_USER,
                        to=recipient_list,
                    )
                    email.attach_alternative(html_msg, "text/html")
                    email.attach(f'receipt_{p_id}.pdf', pdf_data, 'application/pdf')
                    email.send(fail_silently=True)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    
            email_thread = threading.Thread(
                target=send_async_receipt,
                args=(subject, plain_message, html_message, [patient_user.email], pdf_bytes, payment_obj.id)
            )
            email_thread.start()

        return redirect('payment_success', invoice_id=invoice.id)
    
    context = {
        'invoice': invoice,
        'method': method,
        'method_name': dict(Payment.PAYMENT_METHODS).get(method.upper(), method)
    }
    return render(request, 'payment_process.html', context)

@login_required
def payment_success(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can view payment success
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return HttpResponseForbidden("You can only view your own payment receipts.")
    else:
        return HttpResponseForbidden("Only patients can view payment receipts.")
    
    payment = invoice.payments.last()
    return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment})

# ==============================================================================
# FEATURE: RECEIPT GENERATION (PDF)
# PURPOSE: Dynamically generates a PDF receipt for a successful payment using 
#          ReportLab and returns it as an inline HTTP response.
# ==============================================================================
def generate_receipt_pdf_bytes(payment):
    invoice = payment.invoice
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=1
    )
    
    # Title
    elements.append(Paragraph("Payment Receipt", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt Info
    info_data = [
        ['Receipt #:', str(payment.id), 'Date:', payment.timestamp.strftime('%Y-%m-%d')],
        ['Transaction ID:', payment.transaction_id, 'Time:', payment.timestamp.strftime('%H:%M')],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Patient Info
    elements.append(Paragraph("<b>Patient Information:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    patient_data = [
        ['Name:', invoice.patient.name],
        ['Phone:', invoice.patient.phone],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 4.5*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment Details
    elements.append(Paragraph("<b>Payment Details:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Check if we have new line items
    line_items = invoice.line_items.all()
    items_desc = ""
    if line_items.exists():
        items_desc = ", ".join([f"{item.description} (${item.amount})" for item in line_items])
    else:
        items_desc = invoice.items or "N/A"

    payment_data = [
        ['Invoice ID:', f'#{invoice.id}'],
        ['Items:', items_desc],
        ['Payment Method:', payment.get_method_display()],
        ['Amount Paid:', f'${payment.amount}'],
    ]
    
    payment_table = Table(payment_data, colWidths=[1.5*inch, 4.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#dbeafe')),
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Paragraph("<i>Thank you for choosing MediCare!</i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

@login_required
def payment_receipt_pdf(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    pdf_bytes = generate_receipt_pdf_bytes(payment)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{payment_id}.pdf"'
    response.write(pdf_bytes)
    
    return response

from django.utils import timezone

# ==============================================================================
# FEATURE: INVOICE APPROVAL
# PURPOSE: Allows Managers and Admins to approve generated invoices before 
#          patients can pay them.
# ==============================================================================
@login_required
def invoice_approve(request, invoice_id):
    # Only Admin or Manager can approve
    has_permission = False
    if request.user.is_superuser or request.user.role == 'admin':
        has_permission = True
    elif request.user.role == 'staff' and hasattr(request.user, 'staff_profile'):
        if request.user.staff_profile.sub_role == 'manager':
            has_permission = True
            
    if not has_permission:
        return render(request, 'error_403.html', {'message': "You don't have permission to approve invoices."})
        
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if not invoice.is_approved:
        invoice.is_approved = True
        invoice.approved_by = request.user
        invoice.approved_at = timezone.now()
        invoice.save()
        
    return redirect('invoice_detail', pk=invoice_id)
