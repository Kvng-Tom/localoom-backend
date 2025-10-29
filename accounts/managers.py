from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils import normalize_phone_number

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError("Please enter either an email address or a phone number.")

        if email:
            email = self.normalize_email(email)
        if phone_number:
            extra_fields["phone_number"] = normalize_phone_number(phone_number)

        user = self.model(email=email, **extra_fields)
        if password:
            try:
                validate_password(password)
                user.set_password(password)
            except ValidationError as e:
                raise ValueError("Password too weak. It must be at least 8 characters.")
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Superusers must have an email address")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)

    def get_by_identifier(self, identifier: str):
        qs = self.get_queryset()
        if "@" in identifier:
            return qs.filter(email__iexact=identifier).first()
        return qs.filter(phone_number=identifier).first()
