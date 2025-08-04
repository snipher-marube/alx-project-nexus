import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.conf import settings

# Import CloudinaryField only if not in DEBUG mode
if not settings.DEBUG:
    from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    """Custom user model manager with email as primary identifier"""
    
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with email and password"""
        if not email:
            raise ValidationError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        
        if not extra_fields.get('username'):
            extra_fields['username'] = self._generate_unique_username(email)
        
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('user_type') != 'ADMIN':
            raise ValueError(_('Superuser must have user_type set to ADMIN.'))
        if not password:
            raise ValueError(_('Superuser must have a password.'))
        
        return self._create_user(email, password, **extra_fields)

    def _generate_unique_username(self, email):
        """Generate unique username from email"""
        base = slugify(email.split('@')[0].replace('.', '_'))
        username = base
        counter = 1
        
        while self.model.objects.filter(username=username).exists():
            username = f"{base}_{counter}"
            counter += 1
            
        return username

class User(AbstractUser):
    """Custom user model with extended fields"""
    
    class UserType(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer')
        VENDOR = 'VENDOR', _('Vendor')
        ADMIN = 'ADMIN', _('Administrator')
        STAFF = 'STAFF', _('Staff')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Will be generated automatically if not provided'),
    )
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("This email is already registered."),
        },
    )
    
    phone = PhoneNumberField(
        _('phone number'),
        blank=False,
        null=False,
        unique=True,
        error_messages={
            'unique': _("This phone number is already registered."),
        },
    )
    
    user_type = models.CharField(
        _('user type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
    )

    is_verified = models.BooleanField(
        _('verified status'),
        default=False,
        help_text=_('Designates whether the user has verified their email.'),
    )
    
    # Security fields
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        blank=True,
        null=True,
    )
    
    password_changed_at = models.DateTimeField(
        _('password changed at'),
        null=True,
        blank=True,
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        editable=False,
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'user_type']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.get_full_name() or self.email

    def clean(self):
        super().clean()
        if not self.first_name or not self.last_name:
            raise ValidationError(_("First name and last name are required."))

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = User.objects._generate_unique_username(self.email)
        super().save(*args, **kwargs)

    


class Profile(models.Model):
    """Extended user profile information"""
    
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        PREFER_NOT_TO_SAY = 'N', _('Prefer not to say')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=Gender.choices,
        blank=True,
        null=True,
    )
    
    date_of_birth = models.DateField(
        _('date of birth'),
        blank=True,
        null=True,
    )
    # use CloudinaryField if not in DEBUG mode
    if not settings.DEBUG:
        profile_picture = CloudinaryField(
            'image',
            blank=True,
            null=True
    )
    else:
        profile_picture = models.ImageField(
            _('profile picture'),
            upload_to='profile_pictures/%Y/%m/',
            blank=True,
            null=True,
            validators=[
                FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            ],
            help_text=_('Maximum file size: 2MB. JPG, JPEG, or PNG only.'),
        )
    
    bio = models.TextField(
        _('biography'),
        blank=True,
        max_length=500,
    )
    
    address = models.TextField(
        _('address'),
        blank=True,
        max_length=255,
    )
    
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
    )
    
    state = models.CharField(
        _('state/province'),
        max_length=100,
        blank=True,
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
    )
    
    postal_code = models.CharField(
        _('postal code'),
        max_length=20,
        blank=True,
    )
    
    website = models.URLField(
        _('website'),
        blank=True,
    )
    
    social_media = models.JSONField(
        _('social media links'),
        blank=True,
        null=True,
        default=dict,
    )
    
    preferences = models.JSONField(
        _('user preferences'),
        blank=True,
        null=True,
        default=dict,
    )
    
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
    )
    
    push_notifications = models.BooleanField(
        _('push notifications'),
        default=True,
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['country', 'city']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def get_full_address(self):
        """Return formatted full address"""
        parts = [
            self.address,
            self.city,
            self.state,
            self.country,
            self.postal_code
        ]
        return ', '.join(filter(None, parts))

