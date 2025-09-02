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
from .utils import generate_otp, send_email_via_useplunk
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
            serializer.save()
            return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account not verified. Please verify via OTP."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "message": f"Successfully logged in as {user.full_name}",
            "access": str(access),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


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
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=404)

        # Delete old forgot-password OTPs
        OTP.objects.filter(user=user, purpose="forgot-password").delete()

        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=user,
            purpose="forgot-password",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        send_email_via_useplunk(
            to_email=user.email,
            event="forgot-password",
            data={
                "full_name": user.full_name,
                "otp": str(otp_code)
            }
        )

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data['otp']
        password = serializer.validated_data['password']

        try:
            otp_entry = OTP.objects.get(otp=otp, purpose="forgot-password", expiry_date__gt=timezone.now())
        except OTP.DoesNotExist:
            return Response({"error": "Invalid or expired OTP."}, status=400)

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
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.get(user=user, otp=otp, purpose="signup")
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "Invalid email or OTP."}, status=400)

        if not otp_entry.is_valid_now():
            return Response({"error": "OTP expired."}, status=400)

        user.is_active = True
        user.save()
        otp_entry.delete()

        return Response({"message": "Account verified and activated."}, status=200)

class ResendSignupOTPView(APIView):
    @swagger_auto_schema(request_body=ResendOTPSerializer)
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"error": "User is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete old signup OTPs
        OTP.objects.filter(user=user, purpose="signup").delete()

        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=user,
            purpose="signup",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        send_email_via_useplunk(
            to_email=user.email,
            event="user-signup",
            data={
                "full_name": user.full_name,
                "otp": str(otp_code)
            }
        )

        return Response({"message": "New signup OTP sent successfully."}, status=status.HTTP_200_OK)


class ResendForgotPasswordOTPView(APIView):
    @swagger_auto_schema(request_body=ResendOTPSerializer)
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Delete old forgot-password OTPs
        OTP.objects.filter(user=user, purpose="forgot-password").delete()

        otp_code = generate_otp()
        OTP.objects.create(
            otp=str(otp_code),
            user=user,
            purpose="forgot-password",
            expiry_date=timezone.now() + timedelta(minutes=10)
        )

        send_email_via_useplunk(
            to_email=user.email,
            event="forgot-password",
            data={
                "full_name": user.full_name,
                "otp": str(otp_code)
            }
        )

        return Response({"message": "New forgot-password OTP sent successfully."}, status=status.HTTP_200_OK)

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
