from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from django.utils.html import format_html
from .models import Invoice, InvoiceItem, Payment

class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('id', 'patient', 'total_amount_display', 'date', 'status_align')
    list_filter = ('status', 'date')
    inlines = [InvoiceItemInline]
    readonly_fields = ('date',)

    fieldsets = (
        ('Invoice Details', {
            'fields': ('patient', 'date', 'status', 'total_amount'),
            'classes': ['tab']
        }),
    )

    def changelist_view(self, request, extra_context=None):
        from django.db.models import Sum
        extra_context = extra_context or {}
        extra_context['kpi_total_invoices'] = Invoice.objects.count()
        extra_context['kpi_total_revenue'] = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        extra_context['kpi_unpaid'] = Invoice.objects.filter(status='unpaid').count()
        return super().changelist_view(request, extra_context=extra_context)

    def status_align(self, obj):
        badge_map = {
            'unpaid': 'badge-danger',
            'partial': 'badge-warning',
            'paid': 'badge-success',
        }
        badge_class = badge_map.get(obj.status, 'badge-neutral')
        return format_html('<span class="saas-badge {}">{}</span>', badge_class, obj.status.title())
    status_align.short_description = "Status"
    
    def total_amount_display(self, obj):
        return format_html('<div class="text-left font-bold text-gray-500">${}</div>', obj.total_amount)
    total_amount_display.short_description = "Total Amount"

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('transaction_id', 'invoice', 'method', 'amount', 'timestamp')
    list_filter = ('method', 'timestamp')

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.can_manage_billing()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role == 'admin')

