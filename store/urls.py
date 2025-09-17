from django.urls import path
from .views import (
    StorefrontListView, StorefrontDetailView, 
    MyStorefrontView, ProductCreateView, ProductUpdateDeleteView
)

urlpatterns = [
    # Buyers
    path("storefronts/", StorefrontListView.as_view(), name="storefront-list"),
    path("storefronts/<int:pk>/", StorefrontDetailView.as_view(), name="storefront-detail"),

    # Artisans
    path("my-storefront/", MyStorefrontView.as_view(), name="my-storefront"),
    path("products/add/", ProductCreateView.as_view(), name="product-add"),
    path("products/<int:pk>/", ProductUpdateDeleteView.as_view(), name="product-update-delete"),
]
