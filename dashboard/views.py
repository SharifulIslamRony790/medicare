import datetime
import json
from django.utils import timezone
from django.db.models import Sum
from patients.models import Patient
from appointments.models import Appointment
from billing.models import Invoice
from doctors.models import Doctor

# ==============================================================================
# FEATURE: ADMIN DASHBOARD
# PURPOSE: Calculates Key Performance Indicators (KPIs) and recent activities 
#          to be displayed on the Unfold admin dashboard.
# ==============================================================================
def dashboard_callback(request, context):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    total_patients = Patient.objects.count()
    appointments_today = Appointment.objects.filter(date=today).count()
    active_doctors = Doctor.objects.count()
    
    monthly_revenue = Invoice.objects.filter(
        date__gte=first_day_of_month,
        status='Paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Recent activity
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    
    # Chart Data (Revenue for last 7 days)
    labels = []
    revenue_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        labels.append(day.strftime("%b %d"))
        day_rev = Invoice.objects.filter(date=day, status='Paid').aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_data.append(float(day_rev))

    context.update({
        "kpi_patients": total_patients,
        "kpi_appointments": appointments_today,
        "kpi_doctors": active_doctors,
        "kpi_revenue": monthly_revenue,
        "recent_appointments": recent_appointments,
        "chart_labels": json.dumps(labels),
        "chart_data": json.dumps(revenue_data),
    })
    return context

import io
import xlsxwriter
from django.http import HttpResponse

# ==============================================================================
# FEATURE: EXCEL REPORT GENERATION
# PURPOSE: Generates a styled Excel sheet containing monthly revenue data,
#          including a dynamically scaled column chart, using xlsxwriter.
# ==============================================================================
def download_monthly_revenue_excel(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    invoices = Invoice.objects.filter(
        date__gte=first_day_of_month,
        status='Paid'
    ).order_by('date')

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Monthly Revenue')

    # --- Formats ---
    # Title & Subtitle
    title_format = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': '#1E3A8A', 'align': 'center', 'valign': 'vcenter'
    })
    subtitle_format = workbook.add_format({
        'font_size': 11, 'font_color': '#6B7280', 'align': 'center', 'valign': 'vcenter'
    })
    
    # Headers
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#4F46E5', 'font_color': 'white', 
        'border': 1, 'border_color': '#3730A3', 'align': 'center', 'valign': 'vcenter'
    })
    
    # Data Rows (Alternating colors)
    cell_format_1 = workbook.add_format({
        'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'text_wrap': True
    })
    cell_format_2 = workbook.add_format({
        'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'text_wrap': True, 'bg_color': '#F9FAFB'
    })
    
    money_format_1 = workbook.add_format({
        'num_format': '$#,##0.00', 'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'align': 'right'
    })
    money_format_2 = workbook.add_format({
        'num_format': '$#,##0.00', 'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'bg_color': '#F9FAFB', 'align': 'right'
    })
    
    date_format_1 = workbook.add_format({
        'num_format': 'yyyy-mm-dd', 'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'align': 'center'
    })
    date_format_2 = workbook.add_format({
        'num_format': 'yyyy-mm-dd', 'valign': 'vcenter', 'border': 1, 'border_color': '#D1D5DB', 'bg_color': '#F9FAFB', 'align': 'center'
    })

    # Summary section
    summary_label_fmt = workbook.add_format({
        'bold': True, 'bg_color': '#EEF2FF', 'border': 1, 'border_color': '#A5B4FC', 'align': 'right', 'valign': 'vcenter'
    })
    summary_val_fmt = workbook.add_format({
        'bold': True, 'bg_color': '#EEF2FF', 'border': 1, 'border_color': '#A5B4FC', 'num_format': '$#,##0.00', 'align': 'right', 'valign': 'vcenter'
    })

    # --- Title & Meta ---
    worksheet.merge_range('A1:F1', 'MediCare - Monthly Revenue Report', title_format)
    worksheet.merge_range('A2:F2', f"Report generated on: {today.strftime('%B %d, %Y')}", subtitle_format)
    
    # --- Headers ---
    headers = [
        'Invoice ID', 'Date', 'Patient Name', 'Doctor Name',
        'Billed Items (Name & Amount)', 'Invoice Total'
    ]
    for col_num, header in enumerate(headers):
        worksheet.write(3, col_num, header, header_format)

    # --- Column Widths ---
    worksheet.set_column('A:A', 14)
    worksheet.set_column('B:B', 14)
    worksheet.set_column('C:D', 22)
    worksheet.set_column('E:E', 45)
    worksheet.set_column('F:F', 18)

    row = 4
    daily_revenue = {}
    total_revenue_val = 0.0
    invoice_count = 0
    
    for invoice in invoices:
        # Toggle formats for zebra striping
        c_fmt = cell_format_1 if row % 2 == 0 else cell_format_2
        m_fmt = money_format_1 if row % 2 == 0 else money_format_2
        d_fmt = date_format_1 if row % 2 == 0 else date_format_2

        date_str = invoice.date.strftime("%Y-%m-%d")
        inv_total = float(invoice.total_amount)
        daily_revenue[date_str] = daily_revenue.get(date_str, 0) + inv_total
        total_revenue_val += inv_total
        invoice_count += 1
        
        line_items = invoice.line_items.all()
        
        if not line_items:
            billed_items_str = invoice.items or 'General Services'
        else:
            items_list = [f"• {item.description}: ${float(item.amount):.2f}" for item in line_items]
            billed_items_str = "\n".join(items_list)
            
        worksheet.write(row, 0, f"INV-{invoice.id}", c_fmt)
        worksheet.write_datetime(row, 1, invoice.date, d_fmt)
        worksheet.write(row, 2, invoice.patient.name, c_fmt)
        worksheet.write(row, 3, invoice.appointment.doctor.name if invoice.appointment else 'N/A', c_fmt)
        worksheet.write(row, 4, billed_items_str, c_fmt)
        worksheet.write(row, 5, inv_total, m_fmt)
        row += 1

    # --- Summary Section ---
    last_data_row = row
    row += 1
    worksheet.write(row, 4, "Total Monthly Revenue:", summary_label_fmt)
    if last_data_row > 4:
        worksheet.write_formula(row, 5, f'=SUM(F5:F{last_data_row})', summary_val_fmt, total_revenue_val)
    else:
        worksheet.write(row, 5, 0.0, summary_val_fmt)
        
    row += 1
    worksheet.write(row, 4, "Average Invoice Value:", summary_label_fmt)
    if last_data_row > 4:
        avg_val = total_revenue_val / invoice_count if invoice_count > 0 else 0
        worksheet.write_formula(row, 5, f'=AVERAGE(F5:F{last_data_row})', summary_val_fmt, avg_val)
    else:
        worksheet.write(row, 5, 0.0, summary_val_fmt)

    # --- Chart Creation ---
    if daily_revenue:
        chart_sheet = workbook.add_worksheet('Chart Data')
        chart_sheet.hide()
        
        bold = workbook.add_format({'bold': True})
        chart_sheet.write(0, 0, 'Date', bold)
        chart_sheet.write(0, 1, 'Revenue', bold)
        
        chart_row = 1
        
        # Sort by revenue descending (highest to lowest) to match the image design exactly
        sorted_revenue = sorted(daily_revenue.items(), key=lambda item: item[1], reverse=True)
        
        for d, rev in sorted_revenue:
            chart_sheet.write(chart_row, 0, d)
            chart_sheet.write(chart_row, 1, rev)
            chart_row += 1
            
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name':       'Daily Revenue',
            'categories': ['Chart Data', 1, 0, chart_row-1, 0],
            'values':     ['Chart Data', 1, 1, chart_row-1, 1],
            'fill':       {'color': '#5B9BD5'}, # Light blue from the image
            'border':     {'color': '#41719C'}, # Dark blue border from the image
            'gap':        150, # Standard gap for a balanced look
        })
        
        chart.set_title({'name': 'Daily Revenue (Highest to Lowest)', 'name_font': {'size': 14}})
        chart.set_x_axis({
            'name': 'Date',
            'name_font': {'size': 10}, 
            'num_font': {'size': 9, 'rotation': -45},
            'line': {'color': '#BFBFBF'}
        })
        chart.set_y_axis({
            'num_font': {'size': 9}, 
            'major_gridlines': {'visible': True, 'line': {'color': '#D9D9D9'}},
            'line': {'color': '#BFBFBF'}
        })
        chart.set_legend({'none': True})
        chart.set_chartarea({'border': {'color': '#D9D9D9', 'width': 1}, 'fill': {'color': '#FFFFFF'}})
        chart.set_plotarea({'border': {'none': True}})
        
        # Adjust chart width based on the number of data points so bars aren't too far apart or too wide
        num_days = len(sorted_revenue)
        if num_days <= 3:
            chart.set_size({'width': 400, 'height': 380})
        elif num_days <= 10:
            chart.set_size({'width': 550, 'height': 380})
        else:
            chart.set_size({'width': 700, 'height': 380})
        
        worksheet.insert_chart('H4', chart)

    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Monthly_Revenue_{today.strftime('%b_%Y')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

# ==============================================================================
# FEATURE: CONTACT MESSAGES FRONTEND
# PURPOSE: Allows support agents and managers to view and resolve contact messages
#          from the frontend dashboard.
# ==============================================================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import ContactMessage

@login_required
def contact_message_list(request):
    if not request.user.can_handle_support():
        return render(request, 'error_403.html', {'message': "You don't have permission to view contact messages."})
    
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'contact_message_list.html', {'contact_messages': contact_messages})

@login_required
def resolve_contact_message(request, msg_id):
    if not request.user.can_handle_support():
        return render(request, 'error_403.html', {'message': "You don't have permission to resolve contact messages."})
    
    message = get_object_or_404(ContactMessage, id=msg_id)
    message.is_resolved = True
    message.save()
    return redirect('contact_message_list')
