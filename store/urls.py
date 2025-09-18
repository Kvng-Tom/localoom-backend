from django.urls import path
from .views import (
    StorefrontListView,
    StorefrontDetailView,
    MyStorefrontView,
    ProductCreateView,
    ProductUpdateDeleteView,
    BuyerProfileView,
    ArtisanProfileView,
)

urlpatterns = [
    # --- Artisan endpoints ---
    path("artisan/storefronts/", StorefrontListView.as_view(), name="artisan-storefront-list"),
    path("artisan/storefronts/<int:pk>/", StorefrontDetailView.as_view(), name="artisan-storefront-detail"),
    path("artisan/my-storefront/", MyStorefrontView.as_view(), name="artisan-my-storefront"),

    # --- Artisan product management ---
    path("artisan/products/create/", ProductCreateView.as_view(), name="artisan-product-create"),
    path("artisan/products/<int:pk>/", ProductUpdateDeleteView.as_view(), name="artisan-product-update-delete"),

    # --- Buyer endpoints ---
    path("buyer/profile/", BuyerProfileView.as_view(), name="buyer-profile"),

    # --- Artisan profile endpoint ---
    path("artisan/profile/", ArtisanProfileView.as_view(), name="artisan-profile"),
]
