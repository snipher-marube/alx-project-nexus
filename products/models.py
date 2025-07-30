from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q, F, Avg
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

User = get_user_model()

if not settings.DEBUG:
    from cloudinary.models import CloudinaryField

class Category(models.Model):
    """
    Hierarchical category model for product classification
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'name'],
                name='unique_category_name_per_parent'
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_full_path(self):
        """
        Returns the full hierarchical path of the category
        """
        path = [self.name]
        parent = self.parent
        while parent is not None:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))


class Brand(models.Model):
    """
    Brand model for product manufacturers
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    # use cloudinaryField for image storage if settings.DEBUG is False
    if not settings.DEBUG:
        logo = CloudinaryField(
            'logo',
            resource_type='image',
            null=True,
            blank=True,
            transformation={
                'width': 200,
                'height': 200,
                'crop': 'fill'
            }
        )
    else:
        logo = models.ImageField(
            _('logo'),
            upload_to='brands/logos/',
            null=True,
            blank=True
        )
    is_active = models.BooleanField(_('is active'), default=True)
    website = models.URLField(_('website'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Core product model with inventory tracking
    """
    class ProductStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        ACTIVE = 'active', _('Active')
        ARCHIVED = 'archived', _('Archived')
        OUT_OF_STOCK = 'out_of_stock', _('Out of Stock')

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = models.TextField(_('description'))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name=_('category')
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('brand')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        _('compare at price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    cost_per_item = models.DecimalField(
        _('cost per item'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    sku = models.CharField(
        _('SKU'),
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    barcode = models.CharField(
        _('barcode'),
        max_length=100,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    track_quantity = models.BooleanField(_('track quantity'), default=True)
    continue_selling_when_out_of_stock = models.BooleanField(
        _('continue selling when out of stock'),
        default=False
    )
    weight = models.DecimalField(
        _('weight'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Weight in kilograms')
    )
    is_featured = models.BooleanField(_('is featured'), default=False)
    is_digital = models.BooleanField(_('is digital'), default=False)
    requires_shipping = models.BooleanField(_('requires shipping'), default=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_products',
        verbose_name=_('created by')
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        
        if self.status == self.ProductStatus.ACTIVE and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def clean(self):
        if self.compare_at_price and self.compare_at_price <= self.price:
            raise ValidationError(
                _('Compare at price must be greater than the current price.')
            )

    @property
    def is_in_stock(self):
        if not self.track_quantity:
            return True
        return self.quantity > 0 or self.continue_selling_when_out_of_stock

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(
                ((self.compare_at_price - self.price) / self.compare_at_price) * 100,
                2
            )
        return 0

    @property
    def average_rating(self):
        return self.reviews.aggregate(
            average_rating=Avg('rating')
        )['average_rating'] or 0

    def decrease_inventory(self, amount=1):
        if self.track_quantity:
            if self.quantity < amount:
                raise ValidationError(_('Insufficient inventory'))
            self.quantity = F('quantity') - amount
            self.save(update_fields=['quantity'])
            if self.quantity <= 0 and not self.continue_selling_when_out_of_stock:
                self.status = self.ProductStatus.OUT_OF_STOCK
                self.save(update_fields=['status'])

    def increase_inventory(self, amount=1):
        if self.track_quantity:
            self.quantity = F('quantity') + amount
            if self.status == self.ProductStatus.OUT_OF_STOCK:
                self.status = self.ProductStatus.ACTIVE
                self.save(update_fields=['quantity', 'status'])
            else:
                self.save(update_fields=['quantity'])


class ProductImage(models.Model):
    """
    Product images with ordering support
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('product')
    )
    # Use CloudinaryField for image storage if settings.DEBUG is False
    if not settings.DEBUG:
        image = CloudinaryField(
            'image',
            resource_type='image',
            transformation={
                'width': 800,
                'height': 800,
                'crop': 'limit'
            }
        )
    else:
        image = models.ImageField(
            _('image'),
            upload_to='products/images/'
        )
    alt_text = models.CharField(
        _('alt text'),
        max_length=125,
        blank=True,
        help_text=_('Alternative text for accessibility')
    )
    is_primary = models.BooleanField(_('is primary'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'is_primary'],
                condition=Q(is_primary=True),
                name='unique_primary_image_per_product'
            )
        ]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure no other image is marked as primary
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product variants with different attributes (size, color, etc.)
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('product')
    )
    name = models.CharField(_('name'), max_length=100)
    sku = models.CharField(
        _('SKU'),
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        _('compare at price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    track_quantity = models.BooleanField(_('track quantity'), default=True)
    weight = models.DecimalField(
        _('weight'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Weight in kilograms')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product variant')
        verbose_name_plural = _('product variants')
        ordering = ['name']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def is_in_stock(self):
        if not self.track_quantity:
            return True
        return self.quantity > 0


class ProductAttribute(models.Model):
    """
    Product attributes (color, size, material, etc.)
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product attribute')
        verbose_name_plural = _('product attributes')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    """
    Product attribute values (Red, Blue, Large, Small, etc.)
    """
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_('attribute')
    )
    value = models.CharField(_('value'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product attribute value')
        verbose_name_plural = _('product attribute values')
        ordering = ['attribute', 'value']
        constraints = [
            models.UniqueConstraint(
                fields=['attribute', 'value'],
                name='unique_attribute_value'
            ),
            models.UniqueConstraint(
                fields=['attribute', 'slug'],
                name='unique_attribute_slug'
            )
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.value)
        super().save(*args, **kwargs)


class ProductVariantAttribute(models.Model):
    """
    Linking table between product variants and their attributes
    """
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name=_('variant')
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        verbose_name=_('attribute')
    )
    value = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.CASCADE,
        verbose_name=_('value')
    )

    class Meta:
        verbose_name = _('product variant attribute')
        verbose_name_plural = _('product variant attributes')
        constraints = [
            models.UniqueConstraint(
                fields=['variant', 'attribute'],
                name='unique_variant_attribute'
            )
        ]

    def __str__(self):
        return f"{self.variant} - {self.attribute}: {self.value}"


class ProductReview(models.Model):
    """
    Customer reviews for products
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('product')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews',
        verbose_name=_('user')
    )
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(_('title'), max_length=200)
    comment = models.TextField(_('comment'))
    is_approved = models.BooleanField(_('is approved'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product review')
        verbose_name_plural = _('product reviews')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_user_review_per_product'
            )
        ]

    def __str__(self):
        return f"Review for {self.product.name} by {self.user}"

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError(_('Rating must be between 1 and 5'))


class ProductSpecification(models.Model):
    """
    Technical specifications for products
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name=_('product')
    )
    name = models.CharField(_('name'), max_length=100)
    value = models.CharField(_('value'), max_length=255)
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('product specification')
        verbose_name_plural = _('product specifications')
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name}: {self.value}"