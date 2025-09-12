from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from accounts.models import OTP

User = get_user_model()

class Command(BaseCommand):
    help = "Clean up orphaned OTPs, OutstandingTokens, and BlacklistedTokens for deleted users."

    def handle(self, *args, **kwargs):
        # Clean up OTPs with no existing user
        orphan_otps = OTP.objects.exclude(user__in=User.objects.all())
        deleted_otps_count = orphan_otps.count()
        orphan_otps.delete()

        # Clean up OutstandingTokens with no existing user
        orphan_outstanding = OutstandingToken.objects.exclude(user__in=User.objects.all())
        deleted_outstanding_count = orphan_outstanding.count()

        # Delete related blacklisted tokens first
        blacklisted = BlacklistedToken.objects.filter(token__in=orphan_outstanding)
        deleted_blacklisted_count = blacklisted.count()
        blacklisted.delete()

        # Delete orphan outstanding tokens
        orphan_outstanding.delete()

        self.stdout.write(self.style.SUCCESS(
            f"✅ Cleanup complete: {deleted_otps_count} OTPs, "
            f"{deleted_blacklisted_count} BlacklistedTokens, "
            f"{deleted_outstanding_count} OutstandingTokens deleted."
        ))
