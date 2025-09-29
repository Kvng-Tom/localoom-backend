from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import ArtisanProfile, Product, BuyerProfile, Order
from .serializers import (
    ArtisanProfileSerializer,
    ProductSerializer,
    BuyerProfileSerializer,
    StorefrontSerializer,
    OrderSerializer,
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

# --- List Products for a specific Artisan ---

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100

class ProductSearchListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return Response({
            "products": [
                {
                    "id": prod["id"],
                    "name": prod["name"],
                    "price": prod["price"],
                    "image": prod["images"][0] if prod["images"] else None,
                    "category": prod["category"],
                }
                for prod in serializer.data
            ],
            "pagination": {
                "page": int(request.query_params.get("page", 1)),
                "limit": int(request.query_params.get("limit", self.pagination_class.page_size)),
                "total": queryset.count(),
            }
        })
    
# Order Views ---
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        buyer_profile = self.request.user.buyer_profile
        serializer.save(buyer=buyer_profile)

# --- Order List Views ---
class BuyerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user.buyer_profile)

# --- Artisan Order List Views ---
class ArtisanOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(artisan=self.request.user.artisan_profile)
