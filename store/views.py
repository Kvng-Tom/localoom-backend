from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ArtisanProfile, Product, BuyerProfile
from .serializers import (
    ArtisanProfileSerializer,
    ProductSerializer,
    BuyerProfileSerializer,
    StorefrontSerializer,
)

# --- Buyer Profile Views ---
class BuyerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.buyer_profile

# --- Artisan Profile Views ---
class ArtisanProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ArtisanProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.artisan_profile

# --- Storefront Views ---
class StorefrontListView(generics.ListAPIView):
    queryset = ArtisanProfile.objects.filter(verified=True)
    serializer_class = StorefrontSerializer
    permission_classes = [permissions.AllowAny]

class StorefrontDetailView(generics.RetrieveAPIView):
    queryset = ArtisanProfile.objects.filter(verified=True)
    serializer_class = StorefrontSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

class MyStorefrontView(generics.RetrieveUpdateAPIView):
    serializer_class = ArtisanProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile, _ = ArtisanProfile.objects.get_or_create(
            user=user,
            defaults={"full_name": user.full_name or user.email or user.phone_number}
        )
        return profile

# --- Product Views ---
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "artisan_profile"):
            ArtisanProfile.objects.create(
                user=user,
                full_name=user.full_name,
            )
        serializer.save(storefront=user.artisan_profile)

class ProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"


