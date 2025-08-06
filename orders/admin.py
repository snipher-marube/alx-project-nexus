from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.db.models import Count, Sum, F
from django.contrib.admin import SimpleListFilter
from django import forms
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import (
    Order, OrderItem, ShippingAddress, 
    BillingAddress, OrderStatusHistory, Cart, CartItem
)


class OrderStatusFilter(SimpleListFilter):
    title = _('order status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Order.OrderStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class PaymentStatusFilter(SimpleListFilter):
    title = _('payment status')
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return Order.PaymentStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_status=self.value())
        return queryset


class DateRangeFilter(SimpleListFilter):
    title = _('date range')
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('this_week', _('This week')),
            ('this_month', _('This month')),
            ('this_year', _('This year')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'this_week':
            return queryset.filter(created_at__week=now.isocalendar()[1])
        if self.value() == 'this_month':
            return queryset.filter(created_at__month=now.month)
        if self.value() == 'this_year':
            return queryset.filter(created_at__year=now.year)
        return queryset


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = [
        'product_link', 'variant_link', 'name', 
        'price', 'quantity', 'total_price'
    ]
    readonly_fields = ['product_link', 'variant_link', 'total_price']
    autocomplete_fields = ['product', 'variant']

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:products_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product)
        return '-'
    product_link.short_description = _('Product')

    def variant_link(self, obj):
        if obj.variant:
            url = reverse('admin:products_productvariant_change', args=[obj.variant.id])
            return format_html('<a href="{}">{}</a>', url, obj.variant)
        return '-'
    variant_link.short_description = _('Variant')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = _('Total')


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    max_num = 1
    fields = [
        'first_name', 'last_name', 'company',
        'address_line_1', 'address_line_2',
        'city', 'state', 'postal_code', 'country',
        'phone', 'email', 'get_full_address'
    ]
    readonly_fields = ['get_full_address']

    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = _('Full Address')


class BillingAddressInline(admin.StackedInline):
    model = BillingAddress
    extra = 0
    max_num = 1
    fields = [
        'first_name', 'last_name', 'company',
        'address_line_1', 'address_line_2',
        'city', 'state', 'postal_code', 'country',
        'phone', 'email', 'get_full_address'
    ]
    readonly_fields = ['get_full_address']

    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = _('Full Address')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = [
        'old_status', 'new_status', 'note', 
        'created_by', 'created_at'
    ]
    fields = readonly_fields


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'customer_notes': Textarea(attrs={'rows': 3}),
            'admin_notes': Textarea(attrs={'rows': 3}),
        }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = [
        'number', 'user_link', 'status_badge', 
        'payment_status_badge', 'total_amount',
        'item_count', 'created_at'
    ]
    list_filter = [
        OrderStatusFilter, PaymentStatusFilter, 
        DateRangeFilter, 'created_at'
    ]
    search_fields = [
        'number', 'user__email', 'user__first_name', 'user__last_name',
        'shipping_address__first_name', 'shipping_address__last_name',
        'shipping_address__email', 'shipping_address__phone'
    ]
    list_select_related = ['user']
    readonly_fields = [
        'number', 'created_at', 'updated_at', 
        'paid_at', 'cancelled_at', 'ip_address',
        'subtotal', 'tax', 'shipping_cost', 
        'discount', 'total', 'item_count'
    ]
    fieldsets = (
        (None, {
            'fields': (
                'number', 'user', 'status', 
                'payment_status', 'currency'
            )
        }),
        (_('Financials'), {
            'fields': (
                'subtotal', 'tax', 'shipping_cost',
                'discount', 'total'
            ),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': (
                'item_count', 'ip_address',
                'created_at', 'updated_at',
                'paid_at', 'cancelled_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    inlines = [
        OrderItemInline, 
        ShippingAddressInline, 
        BillingAddressInline,
        OrderStatusHistoryInline
    ]
    actions = [
        'mark_as_processing', 'mark_as_shipped', 
        'mark_as_delivered', 'mark_as_cancelled'
    ]
    date_hierarchy = 'created_at'
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request=request)
        return queryset.annotate(
            _item_count=Count('items', distinct=True)
        ).select_related(
            'user', 'shipping_address', 'billing_address'
        )

    def item_count(self, obj):
        return obj._item_count
    item_count.admin_order_field = '_item_count'
    item_count.short_description = _('Items')

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = _('User')
    user_link.admin_order_field = 'user__email'

    def status_badge(self, obj):
        status_colors = {
            'draft': 'gray',
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'pink',
            'failed': 'black',
            'on_hold': 'yellow'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'

    def payment_status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'authorized': 'blue',
            'paid': 'green',
            'partially_refunded': 'yellow',
            'refunded': 'pink',
            'voided': 'gray',
            'failed': 'red'
        }
        color = status_colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = _('Payment')
    payment_status_badge.admin_order_field = 'payment_status'

    def total_amount(self, obj):
        return format_html(
            '<strong>KSH {}</strong>',
            obj.total
        )
    total_amount.short_description = _('Total')
    total_amount.admin_order_field = 'total'

    

    @admin.action(description=_('Mark selected orders as Processing'))
    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status=Order.OrderStatus.PENDING).update(
            status=Order.OrderStatus.PROCESSING
        )
        self.message_user(
            request,
            _('Successfully marked {} orders as processing.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Mark selected orders as Shipped'))
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status=Order.OrderStatus.PROCESSING).update(
            status=Order.OrderStatus.SHIPPED
        )
        self.message_user(
            request,
            _('Successfully marked {} orders as shipped.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Mark selected orders as Delivered'))
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status=Order.OrderStatus.SHIPPED).update(
            status=Order.OrderStatus.DELIVERED
        )
        self.message_user(
            request,
            _('Successfully marked {} orders as delivered.').format(updated),
            messages.SUCCESS
        )

    @admin.action(description=_('Mark selected orders as Cancelled'))
    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            try:
                order.cancel(reason="Bulk cancellation from admin")
            except ValidationError as e:
                self.message_user(request, str(e), messages.ERROR)
        self.message_user(
            request,
            _('Cancellation requested for selected orders.'),
            messages.SUCCESS
        )

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            OrderStatusHistory.objects.create(
                order=obj,
                old_status=form.initial.get('status'),
                new_status=obj.status,
                created_by=request.user,
                note="Changed via admin interface"
            )
        super().save_model(request, obj, form, change)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product_link', 'variant_link', 'quantity', 'price', 'total_price']
    readonly_fields = ['product_link', 'variant_link', 'total_price']
    autocomplete_fields = ['product', 'variant']

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:products_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product)
        return '-'
    product_link.short_description = _('Product')

    def variant_link(self, obj):
        if obj.variant:
            url = reverse('admin:products_productvariant_change', args=[obj.variant.id])
            return format_html('<a href="{}">{}</a>', url, obj.variant)
        return '-'
    variant_link.short_description = _('Variant')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = _('Total')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'session_key', 'item_count', 'subtotal', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'item_count']
    inlines = [CartItemInline]
    date_hierarchy = 'updated_at'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _item_count=Count('items', distinct=True),
            _subtotal=Sum(F('items__price') * F('items__quantity'))
        ).select_related('user')

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = _('User')
    user_link.admin_order_field = 'user__email'

    def item_count(self, obj):
        return obj._item_count
    item_count.admin_order_field = '_item_count'
    item_count.short_description = _('Items')

    def subtotal(self, obj):
        return obj._subtotal or 0
    subtotal.admin_order_field = '_subtotal'
    subtotal.short_description = _('Subtotal')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'old_status', 'new_status', 'created_by', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__number', 'created_by__email']
    readonly_fields = ['order_link', 'old_status', 'new_status', 'created_by', 'created_at']
    date_hierarchy = 'created_at'

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.number)
    order_link.short_description = _('Order')
    order_link.admin_order_field = 'order__number'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Optional: Register shipping and billing address models if you want to edit them separately
# admin.site.register(ShippingAddress)
# admin.site.register(BillingAddress)