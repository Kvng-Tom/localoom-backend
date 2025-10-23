from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import Cart, Order, OrderItem, ShippingAddress
from .serializers import OrderSerializer


class CheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        shipping_data = request.data.get("shipping_address")

        if not shipping_data:
            return Response({"error": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # --- Get user's cart ---
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # ---Calculate total ---
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # --- 3️⃣ Handle shipping address ---
        if isinstance(shipping_data, dict):
            shipping_address = ShippingAddress.objects.create(user=user, **shipping_data)
        else:
            try:
                shipping_address = ShippingAddress.objects.get(id=shipping_data, user=user)
            except ShippingAddress.DoesNotExist:
                return Response({"error": "Invalid shipping address ID."}, status=status.HTTP_400_BAD_REQUEST)

        # --- Create order ---
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=total_amount,
            payment_status="pending"
        )

        # ---  Move cart items into order items ---
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # --- Clear the cart ---
        cart_items.delete()

        # --- Serialize and respond ---
        serializer = self.get_serializer(order)
        return Response({
            "message": "Order placed successfully.",
            "order": serializer.data
        }, status=status.HTTP_201_CREATED)
