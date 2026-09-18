from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import staff_required
from .models import Staff

# ==============================================================================
# FEATURE: STAFF DASHBOARD
# PURPOSE: Dedicated landing page for staff members, potentially displaying 
#          role-specific actions (like billing for Cashiers, or triage for Nurses).
# ==============================================================================
@login_required
@staff_required
def staff_dashboard(request):
    try:
        staff_profile = request.user.staff_profile
    except Staff.DoesNotExist:
        staff_profile = None
        
    context = {
        'staff_profile': staff_profile,
    }
    return render(request, 'staff_dashboard.html', context)
