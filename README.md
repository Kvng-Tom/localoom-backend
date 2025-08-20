# localoom-backend

1. Register User

URL: /register/

Method: POST

Auth: None

Description: Register a new user and send signup OTP.

Request Body:

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "password123"
}


Response (201):

{
  "message": "User registered successfully. OTP sent to email."
}


Notes: Account inactive until OTP verification.

2. Verify OTP (Signup)

URL: /verify-otp/

Method: POST

Auth: None

Description: Verify OTP for account activation.

Request Body:

{
  "email": "user@example.com",
  "otp": "123456"
}


Response (200):

{
  "message": "Account verified and activated."
}

3. Resend Signup OTP

URL: /resend-signup-otp/

Method: POST

Auth: None

Description: Resend OTP for account verification.

Request Body:

{
  "email": "user@example.com"
}


Response (200):

{
  "message": "New signup OTP sent successfully."
}

4. Login

URL: /login/

Method: POST

Auth: None

Description: Login with email & password.

Request Body:

{
  "email": "user@example.com",
  "password": "password123"
}


Response (200):

{
  "message": "Login successful"
}


Response (403 if not verified):

{
  "error": "Account not verified. Please verify via OTP."
}

5. Forgot Password

URL: /forgot-password/

Method: POST

Auth: None

Description: Request OTP to reset password.

Request Body:

{
  "email": "user@example.com"
}


Response (200):

{
  "message": "OTP sent to your email."
}

6. Resend Forgot Password OTP

URL: /resend-forgot-password-otp/

Method: POST

Auth: None

Description: Resend OTP for password reset.

Request Body:

{
  "email": "user@example.com"
}


Response (200):

{
  "message": "New forgot-password OTP sent successfully."
}

7. Reset Password

URL: /reset-password/

Method: POST

Auth: None

Description: Reset password using OTP.

Request Body:

{
  "otp": "123456",
  "password": "newpassword123"
}


Response (200):

{
  "message": "Password reset successful."
}

8. Profile

URL: /profile/

Method: GET

Auth: JWT Required

Description: Get authenticated user's profile.

Response (200):

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "BUYER",
  "date_joined": "2025-08-14T08:00:00Z"
}

9. Logout

URL: /logout/

Method: POST

Auth: JWT Required

Description: Blacklist refresh token to logout user.

Request Body:

{
  "refresh": "<refresh_token_here>"
}


Response (200):

{
  "message": "Successfully logged out user@example.com."
}


k82hkf 1k

