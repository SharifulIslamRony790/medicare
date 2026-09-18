from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Prescription
from .serializers import PrescriptionSerializer
from .forms import PrescriptionForm, MedicationFormSet
from appointments.models import Appointment
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

# ==============================================================================
# FEATURE: API VIEWS
# PURPOSE: Provides secure REST API endpoints for Prescription data.
# ==============================================================================
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

# ==============================================================================
# FEATURE: PRESCRIPTION MANAGEMENT
# PURPOSE: Handles listing prescriptions (role-based) and allowing doctors to 
#          create new prescriptions for their appointments.
# ==============================================================================
@login_required
def prescription_list(request):
    # Filter to show only logged-in user's prescriptions
    if hasattr(request.user, 'patient_profile'):
        prescriptions = Prescription.objects.filter(appointment__patient=request.user.patient_profile).select_related('appointment', 'appointment__patient', 'appointment__doctor').order_by('-created_at')
    else:
        # Admin/staff can see all prescriptions
        prescriptions = Prescription.objects.all().select_related('appointment', 'appointment__patient', 'appointment__doctor').order_by('-created_at')
    return render(request, 'prescription_list.html', {'prescriptions': prescriptions})

@login_required
def prescription_add(request):
    # Only doctors can create prescriptions
    if request.user.role != 'doctor':
        return render(request, 'error_403.html', {'message': 'Only doctors can write prescriptions.'}, status=403)
        
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = MedicationFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            # Auto-set doctor if logged in as doctor
            if hasattr(request.user, 'doctor_profile'):
                # Ensure the appointment belongs to this doctor
                if prescription.appointment.doctor != request.user.doctor_profile:
                     return render(request, 'error_403.html', {'message': 'You can only write prescriptions for your own appointments.'}, status=403)
            prescription.save()
            formset.instance = prescription
            formset.save()
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
        formset = MedicationFormSet()
        # If doctor, filter appointments to only show their confirmed or completed appointments
        if hasattr(request.user, 'doctor_profile'):
            form.fields['appointment'].queryset = Appointment.objects.filter(
                doctor=request.user.doctor_profile, 
                status__in=['confirmed', 'completed']
            ).order_by('-date')
            
    return render(request, 'prescription_form.html', {'form': form, 'formset': formset})

# ==============================================================================
# FEATURE: PRESCRIPTION PDF GENERATION
# PURPOSE: Dynamically generates a highly styled PDF document of the prescription 
#          using ReportLab, complete with hospital header and medication table.
# ==============================================================================
@login_required
def prescription_pdf(request, pk):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from io import BytesIO
    
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # RBAC Security Check
    if request.user.role == 'patient':
        if prescription.appointment.patient != request.user.patient_profile:
            return render(request, 'error_403.html', {'message': 'You can only view your own prescriptions.'}, status=403)
    elif request.user.role == 'doctor':
        if prescription.appointment.doctor != request.user.doctor_profile:
            return render(request, 'error_403.html', {'message': 'You can only view prescriptions you have issued.'}, status=403)
    
    doctor = prescription.appointment.doctor
    patient = prescription.appointment.patient
    
    buffer = BytesIO()
    # Letter size is 8.5 x 11 inches. With 40pt margins, width = 612 - 80 = 532 pts = ~7.38 inches
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    hospital_style = ParagraphStyle('Hospital', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1d4ed8'), fontName='Helvetica-Bold')
    doc_name_style = ParagraphStyle('DocName', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', alignment=2) # Right align
    doc_info_style = ParagraphStyle('DocInfo', parent=styles['Normal'], fontSize=10, textColor=colors.gray, alignment=2)
    rx_style = ParagraphStyle('Rx', parent=styles['Heading1'], fontSize=28, fontName='Helvetica-Bold', textColor=colors.HexColor('#1d4ed8'))
    
    # Header: Hospital Name (Left), Doctor Info (Right)
    header_data = [
        [Paragraph("MediCare Hospital", hospital_style), 
         [Paragraph(f"Dr. {doctor.name}", doc_name_style), 
          Paragraph(f"{doctor.specialty}", doc_info_style),
          Paragraph(f"Phone: {doctor.phone}", doc_info_style)]]
    ]
    header_table = Table(header_data, colWidths=[4*inch, 3.3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    
    # Thick Blue Line
    line = Table([['']], colWidths=[7.3*inch])
    line.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#1d4ed8'))]))
    elements.append(line)
    elements.append(Spacer(1, 15))
    
    # Patient Info Table
    patient_info = [
        [f"Patient Name: {patient.name}", f"Age: {patient.age} Yrs", f"Gender: {patient.gender.capitalize()}"],
        [f"Date: {prescription.created_at.strftime('%d %b %Y')}", f"Time: {prescription.created_at.strftime('%I:%M %p')}", f"Prescription ID: #{prescription.id}"]
    ]
    p_table = Table(patient_info, colWidths=[3*inch, 2*inch, 2.3*inch])
    p_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.darkslategray),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(p_table)
    
    # Thin Grey Line
    line2 = Table([['']], colWidths=[7.3*inch])
    line2.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey)]))
    elements.append(line2)
    elements.append(Spacer(1, 20))
    
    # Clinical Notes
    if prescription.diagnosis or prescription.symptoms:
        if prescription.symptoms:
            elements.append(Paragraph(f"<b>Symptoms:</b> {prescription.symptoms}", styles['Normal']))
            elements.append(Spacer(1, 5))
        if prescription.diagnosis:
            elements.append(Paragraph(f"<b>Diagnosis:</b> {prescription.diagnosis}", styles['Normal']))
            elements.append(Spacer(1, 15))
            
    # Rx Logo
    elements.append(Paragraph("Rx", rx_style))
    elements.append(Spacer(1, 10))
    
    # Medications
    medications = prescription.medications.all()
    if medications.exists():
        med_data = [['#', 'Medicine Name', 'Dosage', 'Duration', 'Instructions']]
        for idx, med in enumerate(medications, 1):
            med_data.append([
                str(idx),
                Paragraph(f"<b>{med.medicine_name}</b>", styles['Normal']),
                med.dosage,
                med.duration,
                Paragraph(med.instruction or '--', styles['Normal'])
            ])
            
        med_table = Table(med_data, colWidths=[0.3*inch, 2.7*inch, 1.2*inch, 1*inch, 2.1*inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(med_table)
        elements.append(Spacer(1, 20))
    elif prescription.medicines:
        elements.append(Paragraph(prescription.medicines.replace('\n', '<br/>'), styles['Normal']))
        elements.append(Spacer(1, 20))
        
    # Advice
    if prescription.advice:
        elements.append(Paragraph("<b>Advice / Follow-up:</b>", styles['Heading3']))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(prescription.advice.replace('\n', '<br/>'), styles['Normal']))
        
    # Footer / Signature
    elements.append(Spacer(1, 50))
    sig_data = [['', '_________________________'], ['', f'Dr. {doctor.name}']]
    sig_table = Table(sig_data, colWidths=[4.8*inch, 2.5*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    from django.http import FileResponse
    if request.GET.get('download') == '1':
        return FileResponse(buffer, as_attachment=True, filename=f"prescription_{pk}.pdf")
    else:
        return FileResponse(buffer, as_attachment=False, filename=f"prescription_{pk}.pdf")

# ==============================================================================
# FEATURE: PRESCRIPTION PRINT VIEW (HTML)
# PURPOSE: Provides a web-based, printer-friendly HTML view of the prescription
#          as an alternative to the PDF.
# ==============================================================================
@login_required
def prescription_print_view(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # RBAC Security Check
    if request.user.role == 'patient':
        if prescription.appointment.patient != request.user.patient_profile:
            return render(request, 'error_403.html', {'message': 'You can only view your own prescriptions.'}, status=403)
    elif request.user.role == 'doctor':
        if prescription.appointment.doctor != request.user.doctor_profile:
            return render(request, 'error_403.html', {'message': 'You can only view prescriptions you have issued.'}, status=403)
            
    return render(request, 'prescription_print.html', {'prescription': prescription})
