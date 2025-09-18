from rest_framework import serializers
from .models import ArtisanProfile, Product, BuyerProfile

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock_quantity", "category", "images", "is_active", "created_at"]

class StorefrontSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ArtisanProfile   
        fields = [
            "id", "full_name", "phone_number", "country", "state", "craft_type", "about_you", "profile_picture", "verified", "products"
        ]

class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = [
            "id", "full_name", "profile_image", "phone_number", "address", "location", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
class ArtisanProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanProfile
        fields = [
            "id", "full_name", "phone_number", "country", "state", "craft_type", "about_you", "profile_picture",
            "verified", "slug", "created_at", "updated_at",
            "bank_name", "account_number", "account_holder_name"
        ]
        read_only_fields = ["id", "verified", "slug", "created_at", "updated_at"]
    class Meta:
        model = ArtisanProfile
        fields = [
            "id", "full_name", "phone_number", "country", "state", "craft_type", "about_you", "profile_picture", "verified", "slug", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "verified", "slug", "created_at", "updated_at"]