from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ArtisanProfile, BuyerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_profiles(sender, instance, created, **kwargs):
    """
    Automatically create or update artisan/buyer profiles when a User is saved.
    - On creation: generate profile based on user.role
    - On update: sync profile names if full_name changes
    """
    # --- Handle new user ---
    if created:
        if instance.role == "ARTISAN":
            ArtisanProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "display_name": instance.full_name
                    or instance.email
                    or instance.phone_number
                },
            )

        elif instance.role == "BUYER":
            BuyerProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "full_name": instance.full_name or ""
                },
            )

    # --- Handle updates to user ---
    else:
        # Sync artisan profile name
        if instance.role == "ARTISAN" and hasattr(instance, "artisan_profile"):
            profile = instance.artisan_profile
            if profile.display_name != instance.full_name:
                profile.display_name = instance.full_name
                profile.save(update_fields=["display_name"])

        # Sync buyer profile name
        elif instance.role == "BUYER" and hasattr(instance, "buyer_profile"):
            profile = instance.buyer_profile
            if profile.full_name != instance.full_name:
                profile.full_name = instance.full_name
                profile.save(update_fields=["full_name"])
