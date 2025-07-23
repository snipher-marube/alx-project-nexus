from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.db.models import Avg, Count, Sum
from django.contrib.admin import SimpleListFilter
from django import forms
from django.db import models
from django.forms import Textarea

from .models import (
    Category, Brand, Product, ProductImage, 
    ProductVariant, ProductAttribute,
    ProductAttributeValue, ProductVariantAttribute,
    ProductReview, ProductSpecification
)

class InventoryFilter(SimpleListFilter):
    title = 'inventory status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock (< 10)'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(quantity__gt=0)
        if self.value() == 'low_stock':
            return queryset.filter(quantity__lt=10, quantity__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(quantity=0)


class StatusFilter(SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Product.ProductStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'rows': 3}),
        }


class CategoryInline(admin.TabularInline):
    model = Category
    fields = ('name', 'slug', 'is_active')
    extra = 0
    show_change_link = True
    form = CategoryAdminForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('name', 'parent_link', 'is_active', 'product_count', 'full_path')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('full_path', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'is_active')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('description', 'full_path', 'created_at', 'updated_at'),
        }),
    )
    inlines = [CategoryInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _product_count=Count('products', distinct=True)
        )

    def product_count(self, obj):
        return obj._product_count
    product_count.admin_order_field = '_product_count'
    product_count.short_description = 'Products'

    def parent_link(self, obj):
        if obj.parent:
            url = reverse('admin:products_category_change', args=[obj.parent.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return '-'
    parent_link.short_description = 'Parent Category'
    parent_link.admin_order_field = 'parent__name'

    def full_path(self, obj):
        return obj.get_full_path()
    full_path.short_description = 'Full Path'


class BrandAdminForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'rows': 3}),
        }


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    form = BrandAdminForm
    list_display = ('name', 'logo_preview', 'is_active', 'product_count', 'website_link')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Details', {
            'fields': ('description', 'website', 'logo', 'logo_preview')
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _product_count=Count('products', distinct=True)
        )

    def product_count(self, obj):
        return obj._product_count
    product_count.admin_order_field = '_product_count'
    product_count.short_description = 'Products'

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo Preview'

    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return '-'
    website_link.short_description = 'Website'


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ('name', 'value', 'order')
    ordering = ('order',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'alt_text', 'is_primary', 'order')
    readonly_fields = ('image_preview',)
    ordering = ('order',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'sku', 'price', 'compare_at_price', 'quantity', 'in_stock')
    readonly_fields = ('in_stock',)

    def in_stock(self, obj):
        return obj.is_in_stock
    in_stock.boolean = True
    in_stock.short_description = 'In Stock'


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'rows': 5}),
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'name',
        'category_link',
        'brand_link',
        'status',
        'price_display',
        'inventory_status',
        'is_featured',
        'rating',
        'created_at',
    )
    list_filter = (
        StatusFilter,
        InventoryFilter,
        'is_featured',
        'is_digital',
        'requires_shipping',
        'category',
        'brand',
        'created_at',
    )
    search_fields = (
        'name',
        'description',
        'sku',
        'barcode',
        'category__name',
        'brand__name',
    )
    list_select_related = ('category', 'brand')
    list_editable = ('is_featured',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'created_at',
        'updated_at',
        'published_at',
        'inventory_status',
        'discount_percentage',
        'average_rating',
        'primary_image_preview',
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'status', 'published_at')
        }),
        ('Pricing', {
            'fields': (
                'price',
                'compare_at_price',
                'discount_percentage',
                'cost_per_item'
            )
        }),
        ('Inventory', {
            'fields': (
                'sku',
                'barcode',
                'quantity',
                'track_quantity',
                'inventory_status',
                'continue_selling_when_out_of_stock',
            )
        }),
        ('Organization', {
            'fields': (
                'category',
                'brand',
                'is_featured',
            )
        }),
        ('Shipping', {
            'classes': ('collapse',),
            'fields': (
                'weight',
                'is_digital',
                'requires_shipping',
            )
        }),
        ('Media', {
            'fields': ('primary_image_preview',)
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
                'average_rating',
            )
        }),
    )
    inlines = [
        ProductSpecificationInline,
        ProductImageInline,
        ProductVariantInline,
    ]
    actions = ['make_active', 'make_draft', 'clear_inventory']
    autocomplete_fields = ['category', 'brand']
    date_hierarchy = 'created_at'
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _average_rating=Avg('reviews__rating')
        ).select_related('category', 'brand')

    def rating(self, obj):
        return obj._average_rating or '-'
    rating.admin_order_field = '_average_rating'
    rating.short_description = 'Rating'

    def price_display(self, obj):
        if obj.compare_at_price and obj.compare_at_price > obj.price:
            return format_html(
                '<span style="color: #d32f2f; font-weight: bold;">${}</span> '
                '<span style="text-decoration: line-through; color: #777;">${}</span>',
                obj.price,
                obj.compare_at_price
            )
        return f"${obj.price}"
    price_display.short_description = 'Price'

    def inventory_status(self, obj):
        if not obj.track_quantity:
            return format_html('<span style="color: #777;">Not Tracked</span>')
        
        if obj.quantity > 10:
            color = '#388e3c'  # Green
            text = f"In Stock ({obj.quantity})"
        elif obj.quantity > 0:
            color = '#ffa000'  # Amber
            text = f"Low Stock ({obj.quantity})"
        else:
            color = '#d32f2f'  # Red
            text = "Out of Stock"
        
        return format_html('<span style="color: {};">{}</span>', color, text)
    inventory_status.short_description = 'Inventory'

    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:products_category_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'
    category_link.short_description = 'Category'
    category_link.admin_order_field = 'category__name'

    def brand_link(self, obj):
        if obj.brand:
            url = reverse('admin:products_brand_change', args=[obj.brand.id])
            return format_html('<a href="{}">{}</a>', url, obj.brand.name)
        return '-'
    brand_link.short_description = 'Brand'
    brand_link.admin_order_field = 'brand__name'

    def primary_image_preview(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                primary_image.image.url
            )
        return '-'
    primary_image_preview.short_description = 'Primary Image Preview'

    @admin.action(description='Mark selected products as active')
    def make_active(self, request, queryset):
        updated = queryset.update(status=Product.ProductStatus.ACTIVE)
        self.message_user(
            request,
            f'{updated} products were successfully marked as active.'
        )

    @admin.action(description='Mark selected products as draft')
    def make_draft(self, request, queryset):
        updated = queryset.update(status=Product.ProductStatus.DRAFT)
        self.message_user(
            request,
            f'{updated} products were successfully marked as draft.'
        )

    @admin.action(description='Clear inventory for selected products')
    def clear_inventory(self, request, queryset):
        updated = queryset.update(quantity=0)
        queryset.filter(track_quantity=True).update(status=Product.ProductStatus.OUT_OF_STOCK)
        self.message_user(
            request,
            f'Inventory cleared for {updated} products.'
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product_link',
        'user_link',
        'rating_stars',
        'title',
        'is_approved',
        'created_at',
    )
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = (
        'product__name',
        'user__email',
        'user__username',
        'title',
        'comment',
    )
    list_select_related = ('product', 'user')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'disapprove_reviews']

    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'

    def rating_stars(self, obj):
        return format_html(
            '<span style="color: #ffc107;">{}</span>',
            '★' * obj.rating + '☆' * (5 - obj.rating)
        )
    rating_stars.short_description = 'Rating'

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(
            request,
            f'{updated} reviews were successfully approved.'
        )

    @admin.action(description='Disapprove selected reviews')
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(
            request,
            f'{updated} reviews were successfully disapproved.'
        )


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'value_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _value_count=Count('values', distinct=True)
        )

    def value_count(self, obj):
        url = reverse('admin:products_productattributevalue_changelist')
        url += f'?{urlencode({"attribute__id__exact": obj.id})}'
        return format_html('<a href="{}">{}</a>', url, obj._value_count)
    value_count.short_description = 'Values'
    value_count.admin_order_field = '_value_count'


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'slug', 'variant_count', 'created_at')
    list_filter = ('attribute',)
    search_fields = ('value', 'slug', 'attribute__name')
    prepopulated_fields = {'slug': ('value',)}
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _variant_count=Count('productvariantattribute', distinct=True)
        )

    def variant_count(self, obj):
        url = reverse('admin:products_productvariant_changelist')
        url += f'?{urlencode({"attributes__value__id__exact": obj.id})}'
        return format_html('<a href="{}">{}</a>', url, obj._variant_count)
    variant_count.short_description = 'Variants'
    variant_count.admin_order_field = '_variant_count'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_link',
        'sku',
        'price_display',
        'inventory_status',
        'attribute_summary',
    )
    list_filter = ('product', 'track_quantity')
    search_fields = (
        'name',
        'sku',
        'product__name',
    )
    list_select_related = ('product',)
    readonly_fields = ('created_at', 'updated_at', 'inventory_status')
    autocomplete_fields = ['product']

    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'

    def price_display(self, obj):
        if obj.compare_at_price and obj.compare_at_price > obj.price:
            return format_html(
                '<span style="color: #d32f2f; font-weight: bold;">${}</span> '
                '<span style="text-decoration: line-through; color: #777;">${}</span>',
                obj.price,
                obj.compare_at_price
            )
        return f"${obj.price}"
    price_display.short_description = 'Price'

    def inventory_status(self, obj):
        if not obj.track_quantity:
            return format_html('<span style="color: #777;">Not Tracked</span>')
        
        if obj.quantity > 10:
            color = '#388e3c'  # Green
            text = f"In Stock ({obj.quantity})"
        elif obj.quantity > 0:
            color = '#ffa000'  # Amber
            text = f"Low Stock ({obj.quantity})"
        else:
            color = '#d32f2f'  # Red
            text = "Out of Stock"
        
        return format_html('<span style="color: {};">{}</span>', color, text)
    inventory_status.short_description = 'Inventory'

    def attribute_summary(self, obj):
        attributes = obj.attributes.select_related('attribute', 'value')
        return ", ".join(
            f"{attr.attribute.name}: {attr.value.value}"
            for attr in attributes
        )
    attribute_summary.short_description = 'Attributes'


@admin.register(ProductVariantAttribute)
class ProductVariantAttributeAdmin(admin.ModelAdmin):
    list_display = (
        'variant_link',
        'attribute',
        'value',
    )
    list_filter = ('attribute',)
    search_fields = (
        'variant__name',
        'variant__product__name',
        'attribute__name',
        'value__value',
    )
    autocomplete_fields = ['variant', 'attribute', 'value']

    def variant_link(self, obj):
        url = reverse('admin:products_productvariant_change', args=[obj.variant.id])
        return format_html('<a href="{}">{}</a>', url, obj.variant.name)
    variant_link.short_description = 'Variant'
    variant_link.admin_order_field = 'variant__name'