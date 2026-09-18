from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'message')

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.can_handle_support()

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_handle_support()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_handle_support()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')
