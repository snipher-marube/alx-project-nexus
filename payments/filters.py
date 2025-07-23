import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    transaction_id = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status')
    method = django_filters.CharFilter(field_name='method')
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    date_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Payment
        fields = []