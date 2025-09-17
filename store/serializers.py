from rest_framework import serializers
from .models import ArtisanStorefront, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock_quantity", "category", "images", "is_active", "created_at"]

class StorefrontSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ArtisanStorefront   # ✅ FIXED HERE
        fields = ["id", "display_name", "bio", "location", "craft_type", "profile_picture", "verified", "products"]
