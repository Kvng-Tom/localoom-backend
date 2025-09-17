# views.py
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP
from .serializers import (
    UserRegistrationSerializer, 
    LoginSerializer, 
    ProfileSerializer, 
    ForgotPasswordSerializer, 
    ResetPasswordSerializer,
    OTPVerifySerializer,
    ResendOTPSerializer
)
from .utils import generate_otp, send_email_via_useplunk, send_user_otp, get_user_by_identifier

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg import openapi

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')




class UserRegistrationView(APIView):
    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)  # inactive until OTP verified

            # Generate OTP
            otp_code = generate_otp()
            OTP.objects.create(
                otp=otp_code,
                user=user,
                purpose="signup",
                expiry_date=timezone.now() + timedelta(minutes=10),
            )

            # Send OTP via preferred method
            results = send_user_otp(user, otp_code, purpose="signup")

            # Log the registration attempt and OTP sending
            contact_method = "email" if results.get("email") else "phone"
            logger.info(
                "New user registration: %s (role=%s), OTP sent via %s",
                user.email or user.phone_number,
                user.role,
                contact_method,
            )

            message = f"Registration successful! OTP sent via {contact_method}."
            return Response({"message": message}, status=status.HTTP_201_CREATED)

        # Log failed registration attempt
        logger.warning("User registration failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        password = serializer.validated_data["password"]

        user = get_user_by_identifier(identifier)
        if not user or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_active:
            return Response({"error": "Account not verified. Verify via OTP."}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": f"Logged in as {user.full_name}",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=200)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"error": "User not found."}, status=404)

        # Delete old forgot-password OTPs
        OTP.objects.filter(user=user, purpose="forgot-password").delete()

        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=user,
            purpose="forgot-password",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        results = send_user_otp(user, otp_code, purpose="forgot-password")

        if results.get("email") or results.get("sms"):
            return Response(
                {"message": f"OTP sent via {'email' if results.get('email') else 'phone'}."},
                status=200
            )
        else:
            return Response(
                {"error": "Failed to send OTP. Please try again later."},
                status=500
            )

class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]
        password = serializer.validated_data["password"]

        try:
            otp_entry = OTP.objects.get(
                otp=otp,
                purpose="forgot-password",
                expiry_date__gt=timezone.now(),
            )
        except OTP.DoesNotExist:
            return Response({"error": "Invalid or expired OTP."}, status=400)

        # Check if blocked
        if otp_entry.blocked_until and timezone.now() < otp_entry.blocked_until:
            return Response({"error": "You are temporarily blocked. Try later."}, status=403)

        user = otp_entry.user
        user.set_password(password)
        user.save()

        otp_entry.delete()
        return Response({"message": "Password reset successful."}, status=200)


class OTPVerifyView(APIView):
    @swagger_auto_schema(request_body=OTPVerifySerializer)
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        otp_code = serializer.validated_data["otp"]

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"error": "User not found."}, status=404)

        otp_entry = OTP.objects.filter(user=user, otp=otp_code, purpose="signup").first()
        if not otp_entry:
            return Response({"error": "Invalid OTP."}, status=400)

        if not otp_entry.is_valid_now():
            return Response({"error": "OTP expired."}, status=400)

        user.is_active = True
        user.save()
        otp_entry.delete()

        return Response({"message": f"OTP verified."}, status=200)

class ResendSignupOTPView(APIView):
    @swagger_auto_schema(request_body=ResendOTPSerializer)
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"]

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"error": "User not found."}, status=404)

        if user.is_active:
            return Response({"error": "User already verified."}, status=400)

        # Delete previous OTPs to avoid duplicates
        OTP.objects.filter(user=user, purpose="signup").delete()

        otp_code = generate_otp()
        OTP.objects.create(
            otp=otp_code,
            user=user,
            purpose="signup",
            expiry_date=timezone.now() + timedelta(minutes=10),
        )

        send_user_otp(user, otp_code, purpose="signup")
        return Response({"message": f"New OTP sent to {'email' if user.email else 'phone'}."}, status=200)

class ResendForgotPasswordOTPView(APIView):
    @swagger_auto_schema(request_body=ResendOTPSerializer)
    def post(self, request):
        identifier = request.data.get("identifier")
        if not identifier:
            return Response({"error": "Identifier is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Delete any previous OTPs for forgot-password to avoid duplicates
        OTP.objects.filter(user=user, purpose="forgot-password").delete()

        otp_code = generate_otp()
        otp_entry = OTP.objects.create(
            otp=otp_code,
            user=user,
            purpose="forgot-password",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        results = send_user_otp(user, otp_code, purpose="forgot-password")

        if results.get("email") or results.get("sms"):
            logger.info(f"Forgot-password OTP sent to user {user.pk} (email: {results.get('email')}, sms: {results.get('sms')})")
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send forgot-password OTP to user {user.pk}")
            return Response({"error": "Failed to send OTP. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Log out user by blacklisting refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Your refresh token'
                )
            },
            required=['refresh']
        ),
        responses={200: 'Logged out successfully', 400: 'Bad request'}
    )
    def post(self, request):
        user = request.user
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": f"Successfully logged out {user.email}."},
                status=200
            )
        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=400)
