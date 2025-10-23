# payments/views.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import VerifyPaymentSerializer, InitializePaymentSerializer
from store.models import Order
from django.utils import timezone


class InitializePaymentView(generics.GenericAPIView):
    serializer_class = InitializePaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # ✅ Only required input: order_id
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Prepare Paystack request
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": request.user.email,
            "amount": int(order.total_amount * 100),  # Convert Naira → Kobo
            "callback_url": "http://localhost:8000/api/payment/verify/"
        }

        response = requests.post(f"{settings.PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
        res_data = response.json()

        if response.status_code != 200 or not res_data.get("status"):
            return Response({"error": res_data.get("message", "Payment initialization failed.")}, status=400)

        reference = res_data["data"]["reference"]

        # ✅ Save Payment record in DB
        Payment.objects.create(
            user=request.user,
            order=order,
            amount=order.total_amount,
            reference=reference
        )

        # ✅ Store reference in order for linkage
        order.payment_reference = reference
        order.save()

        return Response({
            "message": "Payment initialized successfully.",
            "authorization_url": res_data["data"]["authorization_url"],
            "access_code": res_data["data"]["access_code"],
            "reference": reference
        }, status=status.HTTP_200_OK)



# ---- Verify Paystack Payment ----
class VerifyPaymentView(generics.GenericAPIView):
    serializer_class = VerifyPaymentSerializer  
    permission_classes = [IsAuthenticated]

    # 🧩 This adds the query parameter documentation
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'reference',
                openapi.IN_QUERY,
                description="The Paystack payment reference returned after initialization",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={200: "Payment verified successfully."}
    )
    
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data["reference"]

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        response = requests.get(
            f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers
        )
        res_data = response.json()

        if response.status_code != 200 or res_data["data"]["status"] != "success":
            return Response({"error": "Payment verification failed."}, status=400)

        # Mark payment as verified
        try:
            payment = Payment.objects.get(reference=reference)
            payment.verified = True
            payment.save()

            order = payment.order
            order.payment_status = "paid"
            order.transaction_date = timezone.now()
            order.save()
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found."}, status=404)

        return Response(
            {
                "message": "Payment verified successfully.",
                "order_id": order.id,
                "amount": str(payment.amount),
                "reference": reference,
                "status": "paid"
            },
            status=200
        )
