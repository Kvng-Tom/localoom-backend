from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import ArtisanProfile, BuyerProfile, Product, Order

class BuyerProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=BuyerProfile.objects.all(),
                message="Phone number already exists."
            )
        ]
    )
    full_name = serializers.CharField(
        max_length=255,
        error_messages={
            "max_length": "Name is too long (max 255 characters).",
            "blank": "Name cannot be empty."
        }
    )
    

    class Meta:
        model = BuyerProfile
        fields = [
            "full_name",
            "profile_image",
            "phone_number",
            "address",
            "location",
            "created_at",
            "updated_at"
        ]

class ArtisanProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=ArtisanProfile.objects.all(),
                message="Phone number already exists."
            )
        ]
    )
    full_name = serializers.CharField(
        max_length=255,
        error_messages={
            "max_length": "Name is too long (max 255 characters).",
            "blank": "Name cannot be empty."
        }
    )
    

    class Meta:
        model = ArtisanProfile
        fields = [
            "full_name",
            "phone_number",
            "profile_picture",
            "craft_type",
            "about_you",
            "country",
            "state",
            "verified",
            "created_at",
            "updated_at"
        ]

class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=250,
        error_messages={
            "max_length": "Product name is too long (max 250 characters).",
            "blank": "Product name cannot be empty."
        }
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        error_messages={
            "invalid": "Enter a valid price.",
            "min_value": "Price must be greater than zero."
        }
    )
    category = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        error_messages={
            "max_length": "Category name is too long (max 100 characters)."
        }
    )
    stock_quantity = serializers.IntegerField(
        min_value=0,
        error_messages={
            "invalid": "Enter a valid stock quantity.",
            "min_value": "Stock quantity cannot be negative."
        }
    )
    images = serializers.JSONField(
        required=False,
        error_messages={
            "invalid": "Images must be a valid list."
        }
    )
    storefront = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock_quantity",
            "category",
            "images",
            "is_active",
            "created_at",
            "updated_at",
            "storefront"
        ]
class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={
            "required": "Product is required.",
            "does_not_exist": "Selected product does not exist.",
            "incorrect_type": "Invalid product type."
        }
    )
    quantity = serializers.IntegerField(
        min_value=1,
        error_messages={
            "invalid": "Enter a valid quantity.",
            "min_value": "Quantity must be at least 1."
        }
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        error_messages={
            "invalid": "Enter a valid total price.",
            "min_value": "Total price must be greater than zero."
        }
    )
    status = serializers.CharField(
        error_messages={
            "blank": "Order status cannot be empty."
        }
    )
    buyer = serializers.PrimaryKeyRelatedField(read_only=True)
    artisan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "product",
            "quantity",
            "total_price",
            "status",
            "created_at",
            "updated_at",
            "buyer",
            "artisan"
        ]

class StorefrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanProfile
        fields = [
            "id",
            "full_name",
            "profile_picture",
            "craft_type",
            "about_you",
            "country",
            "state",
            "slug",
            "verified"
        ]