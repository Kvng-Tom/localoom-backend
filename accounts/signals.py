from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import OTP
from .utils import generate_otp, send_user_otp

User = get_user_model()

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

        # New unified OTP sending logic
        send_user_otp(instance, otp_code, purpose="user-signup")
