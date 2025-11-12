from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import OTP
from .utils import generate_otp, send_user_otp
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from store.utils import merge_guest_cart  # import the function
User = get_user_model()


# -------------------------------
# OTP on user registration
# -------------------------------
@receiver(post_save, sender=User)
def send_otp_on_registration(sender, instance, created, **kwargs):
    if created and not instance.is_active and not instance.is_superuser:
        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=instance,
            purpose="signup",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        send_user_otp(instance, otp_code, purpose="user-signup")


# -------------------------------
# Cleanup on user delete
# -------------------------------
@receiver(post_delete, sender=User)
def cleanup_user_related(sender, instance, **kwargs):
    # Delete OTPs
    OTP.objects.filter(user=instance).delete()

    # Delete tokens in correct order
    outstanding_tokens = OutstandingToken.objects.filter(user=instance)
    BlacklistedToken.objects.filter(token__in=outstanding_tokens).delete()
    outstanding_tokens.delete()

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """
    Automatically merge the guest cart with the user's cart after login.
    """
    merge_guest_cart(request)