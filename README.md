LocalLoom Accounts Module

This module handles user registration, authentication, and OTP-based verification for the LocalLoom platform. It supports both buyers and artisans, with email and phone number as contact methods.

Features

Custom User Model

Fields: full_name, email, phone_number, role, story, craft_type, location, verified, is_active, is_staff, is_superuser.

Roles: BUYER, ARTISAN, ADMIN.

Email is mandatory for buyers; artisans can register with either email or phone number.

Phone numbers are normalized to +234XXXXXXXXXX format.

Custom User Manager

Handles user creation (create_user) and superuser creation (create_superuser).

Superusers must have an email; phone number is optional only for artisans.

OTP System

OTPs are used for signup verification and password reset.

Each OTP has an expiry time and is unique per user per purpose.

OTP delivery:

Buyers → email only

Artisans → email preferred if available, otherwise SMS

OTP Delivery Services

Email: UsePlunk API

SMS: Termii API

Both have logging for production use.

Account Activation & Verification

Users are created with is_active=False.

After OTP verification, is_active is set to True.

Optional: implement a lockout if OTP fails multiple times.

Password Reset

OTP-based password reset for both email and phone number.

OTPs are single-use and expire after a set period.

Logging

Production-friendly logging setup via Django logging config.

OTP sending, email/SMS success, and failures are logged.

Serializers & Validation

UserRegistrationSerializer: handles user input validation and ensures buyers always use email.

OTPVerifySerializer and ResetPasswordSerializer for OTP flows.

API Views

UserRegistrationView: registers new users.

OTPVerifyView: verifies signup OTP.

ResendSignupOTPView: resend signup OTP (prevents multiple duplicates).

ResendForgotPasswordOTPView: resend forgot password OTP.

ResetPasswordView: reset user password using OTP.

Database Constraints

Unique constraint for OTP per user per purpose.

Proper validation for phone numbers to prevent invalid data.

Installation

Add accounts app to INSTALLED_APPS:

INSTALLED_APPS = [
    ...,
    'accounts',
]


Set the custom user model in settings.py:

AUTH_USER_MODEL = "accounts.User"


Set API keys for OTP delivery:

TERMII_API_KEY = "your_termii_api_key"
USEPLUNK_API_KEY = os.getenv("USEPLUNK_API_KEY")


Run migrations:

python manage.py makemigrations accounts
python manage.py migrate

Usage
Registration

Buyers must provide email.

Artisans can register with either email or phone number.

OTP is automatically sent via the preferred method.

OTP Verification

Users submit OTP along with identifier (email if provided, else phone number).

After successful verification, is_active is set to True.

Password Reset

User requests OTP via email/phone.

Submit OTP along with new password to reset.

Logging

All OTP send events (email and SMS) are logged to production-safe logging handlers.

Errors and warnings are captured to prevent silent failures.

Notes / Recommendations

Use email as the primary contact if available, phone number as fallback.

Avoid storing multiple OTPs simultaneously to prevent MultipleObjectsReturned.

Implement rate-limiting or lockout for multiple OTP failures.

Make logging configurable per environment to avoid verbose logs in production.

Ensure database has proper constraints to prevent duplicate users.
