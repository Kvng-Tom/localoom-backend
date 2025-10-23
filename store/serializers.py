from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import (
    ArtisanProfile,
    BuyerProfile,
    Product,
    Order,
    ProductImage,
    Review,
    Cart,
    ShippingAddress,
    OrderItem,
)
from decimal import Decimal 
import os

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "ds1vagovl")

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

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        image_path = str(obj.image) if obj.image else ""

        if not image_path:
            return None

        # ✅ If it's already a full Cloudinary URL, return it as-is
        if image_path.startswith("http"):
            return image_path

        # ✅ If it starts with "image/upload", don't duplicate it
        if image_path.startswith("image/upload"):
            return f"https://res.cloudinary.com/ds1vagovl/{image_path}"

        # ⚙️ Otherwise, assume Cloudinary path is missing "image/upload/"
        return f"https://res.cloudinary.com/ds1vagovl/image/upload/{image_path}"

    class Meta:
        model = ProductImage
        fields = ["id", "image", "product"]

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Makes user read-only

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at", "updated_at"]
        
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sku = serializers.CharField(read_only=True)
    artisan_location = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)  # Include reviews
    average_rating = serializers.SerializerMethodField()  # Calculate average rating
    storefront = serializers.PrimaryKeyRelatedField(read_only=True)
    slug = serializers.SlugField(read_only=True)  # Include slug field
    
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "stock_quantity",
            "storefront",
            "images",
            "sku",
            "artisan_location",
            "reviews",  # Include reviews
            "average_rating",  # Include average rating
            "slug"  # Include slug field
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None
    
    def get_artisan_location(self, obj):
        artisan = obj.storefront
        if artisan:
            state = artisan.state or ""
            country = artisan.country or ""
            location = f"{state}, {country}".strip(", ")
            return location if location else "Unknown"
        return "Unknown"



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
        min_value=Decimal("0.01"),
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
class MinimalProductSerializer(serializers.ModelSerializer):
    artisan_location = serializers.CharField(source="storefront.location", read_only=True)
    average_rating = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None

    class Meta:
        model = Product
        fields = ["name", "price", "artisan_location", "average_rating"]

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    get_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "get_total"]

    def get_total(self, obj):
        return obj.quantity * obj.price


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ["user"]  


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "shipping_address",
            "items",
            "total_amount",
            "payment_reference",
            "payment_status",
            "transaction_date",
            "created_at",
        ]
        read_only_fields = [
            "total_amount",
            "payment_reference",
            "payment_status",
            "transaction_date",
            "created_at",
            "items",
            "shipping_address",
        ]

