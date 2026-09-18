from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Patient

@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = ('patient_name', 'age', 'gender_align', 'phone', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('gender',)

    fieldsets = (
        ('General Info', {
            'fields': ('user', 'name', 'age', 'gender', 'phone', 'email', 'address', 'image'),
            'classes': ['tab']
        }),
        ('Medical Profile', {
            'fields': ('blood_group', 'medical_history', 'allergies'),
            'classes': ['tab']
        }),
        ('System Info', {
            'fields': ('is_active', 'created_by'),
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
        return request.user.is_authenticated and request.user.can_register_patients()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['kpi_total_patients'] = Patient.objects.count()
        extra_context['kpi_male'] = Patient.objects.filter(gender='Male').count()
        extra_context['kpi_female'] = Patient.objects.filter(gender='Female').count()
        return super().changelist_view(request, extra_context=extra_context)

    def patient_name(self, obj):
        initial = obj.name[0].upper() if obj.name else "?"
        return format_html(
            '<div class="saas-avatar-container">'
            '<div class="saas-avatar avatar-indigo">{}</div>'
            '<span class="saas-avatar-text">{}</span>'
            '</div>', initial, obj.name
        )
    patient_name.short_description = "Patient Name"

    def gender_align(self, obj):
        badge_map = {
            'Male': 'badge-info',
            'Female': 'badge-pink',
            'Other': 'badge-neutral',
        }
        badge_class = badge_map.get(obj.gender, 'badge-neutral')
        return format_html('<span class="saas-badge {}">{}</span>', badge_class, obj.gender)
    gender_align.short_description = "Gender"
