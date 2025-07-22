from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import User, Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update profile when user is saved"""
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


@receiver(pre_save, sender=User)
def update_password_change_date(sender, instance, **kwargs):
    """Update password_changed_at when password changes"""
    if instance.pk:  # Only for existing users
        try:
            original = User.objects.get(pk=instance.pk)
            if original.password != instance.password:
                instance.password_changed_at = timezone.now()
        except User.DoesNotExist:
            pass  # New user being created