# store/models.py
from django.db import models
from django.conf import settings


class ArtisanStorefront(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="storefront"
    )
    display_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    craft_type = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="storefronts/profile_pics/", blank=True, null=True
    )
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artisan Storefront"
        verbose_name_plural = "Artisan Storefronts"

    def __str__(self):
        return f"{self.display_name} ({self.user.email or self.user.phone_number})"


class Product(models.Model):
    storefront = models.ForeignKey(
        ArtisanStorefront,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    images = models.JSONField(default=list, blank=True)  # store multiple image URLs
    is_active = models.BooleanField(default=True)  # product visible or not
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.storefront.display_name})"
