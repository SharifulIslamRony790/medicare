from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(ModelAdmin):
    list_display = ('appointment', 'created_at')

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.can_access_clinical_data()

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_access_clinical_data()

    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.can_access_clinical_data()

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_access_clinical_data()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')
