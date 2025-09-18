from django.urls import path
from .views import (
    MyProductsListView,
    StorefrontListView,
    StorefrontDetailView,
    MyStorefrontView,
    ProductCreateView,
    ProductUpdateDeleteView,
    BuyerProfileView,
    ArtisanProfileView,
    OrderCreateView,
    BuyerOrderListView,
    ArtisanOrderListView,
)

urlpatterns = [
    # --- Artisan endpoints ---
    path("artisan/storefronts/", StorefrontListView.as_view(), name="artisan-storefront-list"),
    path("artisan/storefronts/<int:pk>/", StorefrontDetailView.as_view(), name="artisan-storefront-detail"),
    path("artisan/my-storefront/", MyStorefrontView.as_view(), name="artisan-my-storefront"),

    # --- Artisan product management ---
    path("artisan/products/create/", ProductCreateView.as_view(), name="artisan-product-create"),
    
    path("artisan/products/<int:pk>/", ProductUpdateDeleteView.as_view(), name="artisan-product-update-delete"),
    # List products for a specific artisan
    
    path("artisan/products/", MyProductsListView.as_view(), name="artisan-product-list"),
    # --- Buyer endpoints ---
    path("buyer/profile/", BuyerProfileView.as_view(), name="buyer-profile"),

    # --- Artisan profile endpoint ---
    path("artisan/profile/", ArtisanProfileView.as_view(), name="artisan-profile"),

    # --- Order endpoints ---
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/buyer/", BuyerOrderListView.as_view(), name="buyer-order-list"),
    path("orders/artisan/", ArtisanOrderListView.as_view(), name="artisan-order-list"),
]
