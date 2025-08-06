from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from .models import Payment

class PaymentStatusFilter(admin.SimpleListFilter):
    title = _('payment status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Payment.PaymentStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class PaymentMethodFilter(admin.SimpleListFilter):
    title = _('payment method')
    parameter_name = 'method'

    def lookups(self, request, model_admin):
        return Payment.PaymentMethod.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(method=self.value())
        return queryset

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'order_link',
        'amount_display',
        'currency',
        'method_display',
        'status_badge',
        'is_test',
        'created_at',
        'processed_at',
    ]
    list_filter = [
        PaymentStatusFilter,
        PaymentMethodFilter,
        'is_test',
        'created_at',
        'processed_at'
    ]
    search_fields = [
        'transaction_id',
        'order__number',
        'order__user__email',
        'order__user__first_name',
        'order__user__last_name'
    ]
    readonly_fields = [
        'transaction_id',
        'order_link',
        'amount',
        'currency',
        'method',
        'gateway_response',
        'created_at',
        'processed_at',
        'status_history'
    ]
    fieldsets = (
        (_('Payment Information'), {
            'fields': (
                'transaction_id',
                'order_link',
                'amount',
                'currency',
                'method',
                'status',
                'is_test'
            )
        }),
        (_('Gateway Response'), {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
        (_('Status History'), {
            'fields': ('status_history',),
            'classes': ('collapse',)
        }),
    )
    actions = [
        'mark_as_paid',
        'mark_as_refunded',
        'mark_as_failed',
        'process_refund'
    ]
    date_hierarchy = 'created_at'
    list_select_related = ['order', 'order__user']

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.number)
    order_link.short_description = _('Order')
    order_link.admin_order_field = 'order__number'

    def amount_display(self, obj):
        return format_html('<strong>{} {}</strong>', obj.currency, obj.amount)
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'

    def method_display(self, obj):
        return obj.get_method_display()
    method_display.short_description = _('Method')
    method_display.admin_order_field = 'method'

    def status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'authorized': 'blue',
            'paid': 'green',
            'partially_refunded': 'yellow',
            'refunded': 'purple',
            'voided': 'gray',
            'failed': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def status_history(self, obj):
        # Implement this if you have payment status history tracking
        return "Status history will appear here"
    status_history.short_description = _('Status History')


    @admin.action(description=_('Mark selected payments as paid'))
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status=Payment.PaymentStatus.PENDING).update(
            status=Payment.PaymentStatus.PAID,
            processed_at=timezone.now()
        )
        self.message_user(
            request,
            _('Successfully marked {} payments as paid.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Mark selected payments as refunded'))
    def mark_as_refunded(self, request, queryset):
        updated = queryset.filter(status=Payment.PaymentStatus.PAID).update(
            status=Payment.PaymentStatus.REFUNDED
        )
        self.message_user(
            request,
            _('Successfully marked {} payments as refunded.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Mark selected payments as failed'))
    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status=Payment.PaymentStatus.PENDING).update(
            status=Payment.PaymentStatus.FAILED
        )
        self.message_user(
            request,
            _('Successfully marked {} payments as failed.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Process partial refund for selected payments'))
    def process_refund(self, request, queryset):
        # Implement your refund logic here
        self.message_user(
            request,
            _('Refund processing initiated for selected payments.'),
            messages.INFO
        )

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # Implement status history tracking if needed
            pass
        super().save_model(request, obj, form, change)