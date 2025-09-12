from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.conf import settings

from .managers import UserManager
from .utils import normalize_phone_number  


class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ARTISAN = "ARTISAN", "Artisan"
        BUYER = "BUYER", "Buyer"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(max_length=300, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def clean(self):
        if not self.email and not self.phone_number:
            raise ValidationError("User must have either an email or phone number.")

    def save(self, *args, **kwargs):
        if self.phone_number:
            self.phone_number = normalize_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email or self.phone_number} ({self.role})"

    @property
    def display_name(self):
        return self.full_name

class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("signup", "Signup Verification"),
        ("forgot-password", "Forgot Password"),
    )

    otp = models.CharField(max_length=6)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expiry_date = models.DateTimeField()
    failed_attempts = models.PositiveIntegerField(default=0)  
    resend_count = models.PositiveIntegerField(default=0)     
    blocked_until = models.DateTimeField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid_now(self):
        """Check if OTP is valid and not blocked"""
        if self.blocked_until and timezone.now() < self.blocked_until:
            return False
        return timezone.now() <= self.expiry_date and self.failed_attempts < 3

    def block_for_minutes(self, minutes=30):
        """Block user from OTP actions for X minutes"""
        self.blocked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
