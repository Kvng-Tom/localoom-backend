from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Cart, Order, OrderItem, ShippingAddress
from .serializers import OrderSerializer
from decimal import Decimal

class CheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        shipping_data = request.data.get("shipping_address")

        if not shipping_data:
            return Response(
                {"error": "Shipping address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Fetch user’s cart
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Calculate total amount safely
        total_amount = Decimal("0.00")
        for item in cart_items:
            total_amount += Decimal(item.product.price) * item.quantity

        # ✅ Handle shipping address
        if isinstance(shipping_data, dict):
            shipping_address = ShippingAddress.objects.create(user=user, **shipping_data)
        else:
            try:
                shipping_address = ShippingAddress.objects.get(id=shipping_data, user=user)
            except ShippingAddress.DoesNotExist:
                return Response({"error": "Invalid shipping address ID."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create order with proper total_amount
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_amount=total_amount,
            payment_status="pending"
        )

        # ✅ Move cart items into order items
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # ✅ Clear cart
        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(
            {"message": "Order placed successfully.", "order": serializer.data},
            status=status.HTTP_201_CREATED
        )
