
from rest_framework import serializers
from .models import User
from .utils import normalize_phone_number

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False, "allow_null": True, "allow_blank": True},
            "phone_number": {"required": False, "allow_null": True, "allow_blank": True},
            "role": {"required": True},
        }

    def validate(self, data):
        role = data.get("role")
        email = data.get("email")
        phone = data.get("phone_number")

        # --- Rule for Buyers ---
        if role == User.Roles.BUYER:
            if not email:
                raise serializers.ValidationError({"email": "Buyers must register with an email."})
            # Buyers should not use phone number (optional: strip it out)
            data["phone_number"] = None  

        # --- Rule for Artisans ---
        if role == User.Roles.ARTISAN:
            if not email and not phone:
                raise serializers.ValidationError(
                    {"error": "Artisans must register with either an email or a phone number."}
                )

        # --- Normalize phone (optional if you have util) ---
        if phone:
            data["phone_number"] = normalize_phone_number(phone)

        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        # default inactive until OTP verification
        user.is_active = False
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "full_name",
            "role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["is_active", "date_joined"]

class ForgotPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(max_length=6)

class ResendOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()