from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, Cart
from .serializers import OrderSerializer

class CheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        shipping_info = request.data.get("shipping_info")

        if not shipping_info:
            return Response({"error": "Shipping information is required."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.quantity * item.product.price for item in cart_items)

        # Create the order
        order = Order.objects.create(user=user, shipping_info=shipping_info, total=total)

        # Add cart items to the order
        for item in cart_items:
            order.items.create(product=item.product, quantity=item.quantity, price=item.product.price)

        # Clear the cart
        cart_items.delete()

        return Response({"message": "Order placed successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)