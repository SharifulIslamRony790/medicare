from django.http import HttpResponseForbidden
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has a particular role.
    Usage: @role_required('admin', 'doctor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator

# Convenience decorators
patient_required = role_required('patient')
doctor_required = role_required('doctor')
staff_required = role_required('staff')
