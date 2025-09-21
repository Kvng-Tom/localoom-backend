# store/models.py
from django.db import models
from django.conf import settings


class ArtisanProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artisan_profile"
    )
    CRAFT_CHOICES = [
        ("pottery", "Pottery & Ceramics"),
        ("baskets", "Baskets and Cane"),
        ("textiles", "Textiles and Fibre Weaving"),
        ("woodwork", "Woodwork and Carving"),
        ("beadwork", "Beadwork and Jewelry"),
        ("leather", "Leather Work"),
        ("artwork", "Art Work"),
        ("home", "Home and Lifestyle Crafts"),
    ]

    full_name = models.CharField(max_length=255) 
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    craft_type = models.CharField(
        max_length=50,
        choices=CRAFT_CHOICES,
        blank=True,
        null=True
    )
    about_you = models.TextField(blank=True, null=True) 
    profile_picture = models.ImageField(
        upload_to="artisans/profile_images/", blank=True, null=True
    )
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Artisan Profile"
        verbose_name_plural = "Artisan Profiles"

    def __str__(self):
        return f"{self.full_name} ({self.user.email or self.user.phone_number})"


class Product(models.Model):
    storefront = models.ForeignKey(
        ArtisanProfile,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=250)
    description = models.TextField()
    price =  models.DecimalField(max_digits=10, decimal_places=2)
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

class BuyerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="buyer_profile"
    )
    full_name = models.CharField(max_length=255)
    profile_image = models.ImageField(
        upload_to="buyers/profile_images/", blank=True, null=True
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyer Profile"
        verbose_name_plural = "Buyer Profiles"

    def __str__(self):
        return self.full_name or self.user.email or str(self.user)

class Order(models.Model):
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name="orders")
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=[
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)