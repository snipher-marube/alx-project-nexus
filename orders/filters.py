import django_filters
from django.db.models import Q
from .models import Order


class OrderFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status')
    payment_status = django_filters.CharFilter(field_name='payment_status')
    min_total = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    date_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    customer = django_filters.CharFilter(method='filter_by_customer')

    class Meta:
        model = Order
        fields = []

    def filter_by_customer(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(shipping_address__first_name__icontains=value) |
            Q(shipping_address__last_name__icontains=value) |
            Q(shipping_address__email__icontains=value)
        )


