import django_filters
from django.db.models import Q
from .models import Product, Category, ProductVariant


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    status = django_filters.CharFilter(field_name='status')
    featured = django_filters.BooleanFilter(field_name='is_featured')
    search = django_filters.CharFilter(method='custom_search')

    class Meta:
        model = Product
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(sku__icontains=value) |
            Q(barcode__icontains=value) |
            Q(category__name__icontains=value) |
            Q(brand__name__icontains=value)
        )


class CategoryFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name='is_active')
    parent = django_filters.CharFilter(field_name='parent__slug')

    class Meta:
        model = Category
        fields = []


class ProductVariantFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    attribute = django_filters.CharFilter(method='filter_by_attribute')

    class Meta:
        model = ProductVariant
        fields = []

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(Q(track_quantity=False) | Q(quantity__gt=0))
        return queryset.filter(track_quantity=True, quantity=0)

    def filter_by_attribute(self, queryset, name, value):
        try:
            attr_name, attr_value = value.split(':')
            return queryset.filter(
                attributes__attribute__name=attr_name,
                attributes__value__value=attr_value
            )
        except (ValueError, AttributeError):
            return queryset.none()