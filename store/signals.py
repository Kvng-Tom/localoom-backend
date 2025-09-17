# store/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ArtisanStorefront

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_storefront_for_artisan(sender, instance, created, **kwargs):
    if created and instance.role == "ARTISAN":
        ArtisanStorefront.objects.create(user=instance, display_name=instance.full_name)
