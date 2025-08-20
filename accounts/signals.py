# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import OTP
from .utils import generate_otp, send_email_via_useplunk

User = get_user_model()

@receiver(post_save, sender=User)
def send_otp_on_registration(sender, instance, created, **kwargs):
    
    if created and not instance.is_active and not instance.is_superuser:
        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=instance,
            purpose= "signup",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        send_email_via_useplunk(
            to_email=instance.email,
            event="user-signup", 
            data={
                "full_name": instance.full_name,
                "otp": str(otp_code)
            }
        )
