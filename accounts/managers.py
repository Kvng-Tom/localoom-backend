from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from .utils import normalize_phone_number  # if utils.py has phone normalization


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        """
        Custom create_user:
        - Buyers must always have email (enforced in serializer).
        - Artisans can register with either phone_number or email.
        """
        if not email and not phone_number:
            raise ValueError("The user must have either an email or phone number")

        if email:
            email = self.normalize_email(email)
            extra_fields["email"] = email
        if phone_number:
            extra_fields["phone_number"] = normalize_phone_number(phone_number)

        user = self.model(**extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Superusers are email-only to keep Django admin safe.
        """
        if not email:
            raise ValueError("Superusers must have an email address")

        email = self.normalize_email(email)
        extra_fields.setdefault("email", email)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)

    def get_by_identifier(self, identifier: str):
        """
        Allow fetching user by email or phone_number.
        Example:
            User.objects.get_by_identifier("test@email.com")
            User.objects.get_by_identifier("+2348012345678")
        """
        qs = self.get_queryset()
        if "@" in identifier:
            return qs.filter(email__iexact=identifier).first()
        return qs.filter(phone_number=identifier).first()
