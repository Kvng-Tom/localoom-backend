LocalLoom – Accounts Service

LocalLoom is a backend platform for local business listings and community commerce.
This service handles user authentication and account management, supporting both buyers and artisans.

Features
User registration (Buyer & Artisan roles)
Email verification with OTP
Secure JWT authentication
Forgot/Reset password flow with OTP
Resend OTP (for signup & password reset)
Profile management (view & update)
Logout (token invalidation)
Full API documentation in Swagger UI

Tech Stack
Backend: Django REST Framework
Authentication: JWT (JSON Web Tokens)
Database: SQLite (dev) / PostgreSQL (prod)
Email: SendGrid for OTP delivery
Docs: Swagger UI

API Endpoints
1. User Registration
POST /api/accounts/register/
Buyer Example
{
  "email": "buyer1@example.com",
  "full_name": "Jane Doe",
  "password": "StrongPass123!",
  "role": "BUYER"
}

Artisan Example
{
  "email": "artisan1@example.com",
  "full_name": "Titi Basketweaver",
  "password": "StrongPass123!",
  "role": "ARTISAN",
  "story": "I weave baskets using traditional methods passed down in my village.",
  "craft_type": "Basket Weaving",
  "location": "Lagos, Nigeria"
}
✅ 201 Created + OTP email sent

2. Email Verification (OTP)
POST /api/accounts/verify-otp/
{
  "email": "artisan1@example.com",
  "otp": "123456"
}
✅ Activates user if OTP is valid

3. Login
POST /api/accounts/login/
{
  "email": "artisan1@example.com",
  "password": "StrongPass123!"
}
✅ Returns JWT tokens

4. Forgot Password
POST /api/accounts/forgot-password/
{
  "email": "artisan1@example.com"
}
✅ Sends OTP for reset

5. Reset Password
POST /api/accounts/reset-password/
{
  "otp": "654321",
  "password": "NewStrongPass456!"
}
✅ Updates password

6. Resend OTP
Signup OTP: POST /api/accounts/resend-signup-otp/
Forgot Password OTP: POST /api/accounts/resend-forgot-password-otp/
{
  "email": "artisan1@example.com"
}

7. View Profile
GET /api/accounts/profile/ (JWT required)
{
  "email": "artisan1@example.com",
  "full_name": "Titi Basketweaver",
  "date_joined": "2025-09-01T12:34:56Z",
  "role": "ARTISAN",
  "story": "I weave baskets using traditional methods...",
  "craft_type": "Basket Weaving",
  "location": "Oyo, Nigeria",
  "verified": true
}

8. Update Profile
PUT /api/accounts/profile/ (JWT required)
{
  "full_name": "Titi B. Weaver",
  "story": "Updated story about my craft.",
  "craft_type": "Basket Weaving",
  "location": "Ibadan, Nigeria"
}
✅ Updates profile

9. Logout
POST /api/accounts/logout/ (JWT required)
✅ Invalidates token

Notes
All APIs available in Swagger UI at /swagger/
Use valid emails for OTP-related features
Handle errors: invalid data, expired OTP, unauthorized access
