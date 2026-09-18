from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status_align')
    list_filter = ('status', 'date')
    search_fields = ('patient__name', 'doctor__name')

    fieldsets = (
        ('Schedule', {
            'fields': ('patient', 'doctor', 'date', 'time', 'status'),
            'classes': ['tab']
        }),
        ('System Info', {
            'fields': ('created_by',),
            'classes': ['tab']
        }),
    )

    def has_module_permission(self, request):
        return request.user.is_authenticated and (request.user.can_register_patients() or request.user.can_access_clinical_data())

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.can_register_patients() or request.user.can_access_clinical_data())

    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.can_register_patients()

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.can_register_patients() or request.user.can_access_clinical_data())

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')


    def changelist_view(self, request, extra_context=None):
        from django.utils import timezone
        extra_context = extra_context or {}
        today = timezone.now().date()
        extra_context['kpi_total'] = Appointment.objects.count()
        extra_context['kpi_today'] = Appointment.objects.filter(date=today).count()
        extra_context['kpi_pending'] = Appointment.objects.filter(status='pending').count()
        return super().changelist_view(request, extra_context=extra_context)

    def status_align(self, obj):
        badge_map = {
            'pending': 'badge-warning',
            'confirmed': 'badge-info',
            'completed': 'badge-success',
            'cancelled': 'badge-danger',
        }
        badge_class = badge_map.get(obj.status, 'badge-neutral')
        return format_html('<span class="saas-badge {}">{}</span>', badge_class, obj.status.title())
    status_align.short_description = "Status"
