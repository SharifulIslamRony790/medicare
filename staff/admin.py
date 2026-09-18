from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    list_display = ('name', 'sub_role', 'phone', 'department', 'created_at')
    list_filter = ('sub_role', 'department')
    search_fields = ('name', 'phone', 'user__username', 'user__email')
