from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    fieldsets = (
        ('Account Credentials', {'fields': ('username', 'password'), 'classes': ['tab']}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email', 'role'), 'classes': ['tab']}),
        ('Permissions & Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['tab'],
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined'), 'classes': ['tab']}),
    )

    list_display = ('username_display', 'email', 'role_align', 'is_staff', 'is_active')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['kpi_total_users'] = User.objects.count()
        extra_context['kpi_active_users'] = User.objects.filter(is_active=True).count()
        extra_context['kpi_doctors'] = User.objects.filter(role='doctor').count()
        return super().changelist_view(request, extra_context=extra_context)

    def username_display(self, obj):
        initial = obj.username[0].upper() if obj.username else "?"
        colors = ['blue', 'indigo', 'emerald', 'violet', 'rose', 'cyan', 'amber']
        color = colors[sum(ord(c) for c in obj.username) % len(colors)]
        return format_html(
            '<div class="saas-avatar-container">'
            '<div class="saas-avatar avatar-{}">{}</div>'
            '<span class="saas-avatar-text">{}</span>'
            '</div>', color, initial, obj.username
        )
    username_display.short_description = "Username"

    def role_align(self, obj):
        badge_map = {
            'patient': 'badge-success',
            'doctor': 'badge-info',
            'staff': 'badge-purple',
            'admin': 'badge-danger',
        }
        badge_class = badge_map.get(obj.role, 'badge-neutral')
        return format_html('<span class="saas-badge {}">{}</span>', badge_class, obj.role.title())
    role_align.short_description = "Role"
