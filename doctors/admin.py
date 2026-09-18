from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(ModelAdmin):
    list_display = ('doctor_name', 'specialty_align', 'phone')
    search_fields = ('name', 'specialty')
    list_filter = ('specialty',)

    fieldsets = (
        ('Professional Info', {
            'fields': ('user', 'name', 'specialty', 'image'),
            'classes': ['tab']
        }),
        ('Contact Info', {
            'fields': ('phone',),
            'classes': ['tab']
        }),
    )

    def doctor_name(self, obj):
        initial = obj.name[0].upper() if obj.name else "?"
        return format_html(
            '<div class="saas-avatar-container">'
            '<div class="saas-avatar avatar-emerald">{}</div>'
            '<span class="saas-avatar-text">{}</span>'
            '</div>', initial, obj.name
        )
    doctor_name.short_description = "Doctor Name"

    def specialty_align(self, obj):
        return format_html('<span class="saas-badge badge-purple">{}</span>', obj.specialty)
    specialty_align.short_description = "Specialty"
