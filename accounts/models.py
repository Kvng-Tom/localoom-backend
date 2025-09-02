from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.conf import settings

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ARTISAN = "ARTISAN", "Artisan"
        BUYER = "BUYER", "Buyer"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(max_length=300, unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.BUYER,
        
    )
    
    story = models.TextField(blank=True, null=True)
    craft_type = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def display_name(self):
        return self.full_name


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ('signup', 'Signup Verification'),
        ('forgot-password', 'Forgot Password'),
    )

    otp = models.CharField(max_length=6)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expiry_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid_now(self):
        return timezone.now() <= self.expiry_date

    class Meta:
        unique_together = ('user', 'purpose')  # This ensures one OTP per user per purpose

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.otp}"
    
