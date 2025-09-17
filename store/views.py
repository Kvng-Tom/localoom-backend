from rest_framework import generics, permissions
from .models import ArtisanStorefront, Product   
from .serializers import StorefrontSerializer, ProductSerializer
from .permissions import IsArtisan

# --- Buyers can view artisans ---
class StorefrontListView(generics.ListAPIView):
    queryset = ArtisanStorefront.objects.filter(verified=True)   
    serializer_class = StorefrontSerializer
    permission_classes = [permissions.AllowAny]

class StorefrontDetailView(generics.RetrieveAPIView):
    queryset = ArtisanStorefront.objects.filter(verified=True)   
    serializer_class = StorefrontSerializer
    permission_classes = [permissions.AllowAny]

# --- Artisans manage their own storefront ---
class MyStorefrontView(generics.RetrieveUpdateAPIView):
    serializer_class = StorefrontSerializer
    permission_classes = [IsArtisan]

    def get_object(self):
        return self.request.user.storefront

# --- Artisans manage products ---
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsArtisan]

    def perform_create(self, serializer):
        user = self.request.user

        # This ensures the artisan has a storefront
        if not hasattr(user, "storefront"):
            from .models import ArtisanStorefront
            ArtisanStorefront.objects.create(user=user, display_name=user.full_name)
            
        serializer.save(storefront=user.storefront)

class ProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsArtisan]

    def get_queryset(self):
        return Product.objects.filter(storefront=self.request.user.storefront)
