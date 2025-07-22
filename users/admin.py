from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from .models import User, Profile

# Unregister default Group model if you're not using Django's built-in groups
admin.site.unregister(Group)


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'
    readonly_fields = ('created_at', 'updated_at', 'profile_picture_display')
    fieldsets = (
        (_('Personal Info'), {
            'fields': ('gender', 'date_of_birth', 'profile_picture_display', 'profile_picture', 'bio')
        }),
        (_('Contact Information'), {
            'fields': ('address', 'city', 'state', 'country', 'postal_code', 'website')
        }),
        (_('Preferences'), {
            'fields': ('social_media', 'preferences', 'email_notifications', 'push_notifications')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def profile_picture_display(self, instance):
        if instance.profile_picture:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 50%;" />',
                instance.profile_picture.url
            )
        return _("No profile picture")
    profile_picture_display.short_description = _('Current Picture')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'get_full_name', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'user_type', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'created_at', 'updated_at', 'password_changed_at')
    actions = ['activate_users', 'deactivate_users']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'username', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'user_type', 'groups', 'user_permissions'),
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'password_changed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Security'), {
            'fields': ('last_login_ip',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    get_full_name.admin_order_field = 'first_name'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True
        
        return form
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _('Successfully activated %(count)d users') % {'count': updated})
    activate_users.short_description = _('Activate selected users')
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('Successfully deactivated %(count)d users') % {'count': updated})
    deactivate_users.short_description = _('Deactivate selected users')
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_full_name', 'gender', 'age', 'country', 'city', 'created_at')
    list_filter = ('gender', 'country', 'city', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'address', 'city', 'country')
    readonly_fields = ('user_link', 'created_at', 'updated_at', 'age', 'profile_picture_display')
    fieldsets = (
        (None, {
            'fields': ('user_link', 'gender', 'date_of_birth', 'age')
        }),
        (_('Profile Picture'), {
            'fields': ('profile_picture_display', 'profile_picture'),
            'classes': ('collapse',)
        }),
        (_('Biography'), {
            'fields': ('bio',),
            'classes': ('collapse',)
        }),
        (_('Location'), {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        (_('Contact'), {
            'fields': ('website', 'social_media')
        }),
        (_('Preferences'), {
            'fields': ('preferences', 'email_notifications', 'push_notifications')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = _('Full Name')
    user_full_name.admin_order_field = 'user__first_name'
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = _('User')
    
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return _("No profile picture")
    profile_picture_display.short_description = _('Current Picture')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Admin site customization
admin.site.site_header = _('E-Commerce Administration')
admin.site.site_title = _('E-Commerce Admin Portal')
admin.site.index_title = _('Welcome to E-Commerce Admin')

# Register models
admin.site.register(User, UserAdmin)

# Optional: Customize LogEntry admin if you want to track admin actions
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('action_time', 'content_type', 'action_flag')
    search_fields = ('user__email', 'object_repr', 'change_message')
    date_hierarchy = 'action_time'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')