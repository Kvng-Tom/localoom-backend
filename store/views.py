from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ArtisanProfile, Product, BuyerProfile, Order, Review
from .serializers import (
    ArtisanProfileSerializer,
    ProductSerializer,
    BuyerProfileSerializer,
    StorefrontSerializer,
    OrderSerializer,
    ProductImageSerializer,
    ReviewSerializer
)
from rest_framework import serializers

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
    
class MyProductsListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(storefront=user.artisan_profile)
    
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


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.request.data.get("product")

        # Check if product_id is provided
        if not product_id:
            raise serializers.ValidationError({"product": "Product ID is required."})

        try:
            # Try to fetch the product
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            # Return a meaningful error if the product does not exist
            raise serializers.ValidationError({"product": "Product with the given ID does not exist."})

        # Save the product image
        serializer.save(product=product)

# --- Pagination for Product List ---
class ProductPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = "limit"  # Allow clients to specify page size
    max_page_size = 100  # Maximum number of items per page

# --- List All Products with Pagination ---
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ProductPagination  

    def get_queryset(self):
        sort_by = self.request.query_params.get("sort_by", "created_at")
        sort_order = self.request.query_params.get("sort_order", "asc")
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")  

        valid_sort_fields = ["price", "created_at", "name", "sales_count"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        queryset = Product.objects.all()

        if category:
            queryset = queryset.filter(category__iexact=category)  

        if search:
            queryset = queryset.filter(name__icontains=search)  

        return queryset.order_by(sort_by)

# --- Review Views ---
class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Review.objects.filter(product_id=product_id)

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
