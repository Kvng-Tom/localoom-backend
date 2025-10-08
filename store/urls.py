from django.urls import path
from .views import (
    ProductImageUploadView,
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
    ProductSearchListView,
    MyProductsListView,
    ProductListView,
    ReviewListView,
    ReviewCreateView,
    MinimalProductListView,
)

urlpatterns = [
    # --- Public product search & list ---
    path("products/", ProductSearchListView.as_view(), name="product-search-list"),
    # --- Public product list ---
    path("products/all/", ProductListView.as_view(), name="product-list"),
    path("products/minimal/", MinimalProductListView.as_view(), name="minimal-product-list"),

    # --- Artisan endpoints ---
    path("artisan/storefronts/", StorefrontListView.as_view(), name="artisan-storefront-list"),
    path("artisan/storefronts/<int:pk>/", StorefrontDetailView.as_view(), name="artisan-storefront-detail"),
    path("artisan/my-storefront/", MyStorefrontView.as_view(), name="artisan-my-storefront"),

    # --- Artisan product management ---
    path("artisan/products/create/", ProductCreateView.as_view(), name="artisan-product-create"),
    path("artisan/products/<slug:slug>/", ProductUpdateDeleteView.as_view(), name="artisan-product-update-delete"),
    path("artisan/products/", MyProductsListView.as_view(), name="artisan-products-list"),
    path("artisan/products/upload-image/", ProductImageUploadView.as_view(), name="product-image-upload"),
    
    # --- Buyer endpoints ---
    path("buyer/profile/", BuyerProfileView.as_view(), name="buyer-profile"),

    # --- Artisan profile endpoint ---
    path("artisan/profile/", ArtisanProfileView.as_view(), name="artisan-profile"),

    # -- Order endpoints ---
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/buyer/", BuyerOrderListView.as_view(), name="buyer-order-list"),
    path("orders/artisan/", ArtisanOrderListView.as_view(), name="artisan-order-list"),

    # --- Review endpoints ---
    path("products/<int:product_id>/reviews/", ReviewListView.as_view(), name="product-reviews"),
    path("products/reviews/create/", ReviewCreateView.as_view(), name="create-review"),
    path("products/<slug:slug>/", ProductUpdateDeleteView.as_view(), name="product-detail"),
]
