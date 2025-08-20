from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    ForgotPasswordView,
    ResetPasswordView,
    OTPVerifyView,
    ResendSignupOTPView,
    ResendForgotPasswordOTPView,
    LogoutView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('logout', LogoutView.as_view(), name='logout'),
    
    path('resend-signup-otp/', ResendSignupOTPView.as_view(), name='resend-signup-otp'),
    path('resend-forgot-password-otp/', ResendForgotPasswordOTPView.as_view(), name='resend-forgot-password-otp'),
]
