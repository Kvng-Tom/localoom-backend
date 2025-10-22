import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer
from store.models import Order
from django.utils import timezone

# ---- Initialize Paystack payment ----
class InitializePaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize payment on Paystack
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": request.user.email,
            "amount": int(order.total_amount * 100),  # Convert to kobo
            "callback_url": "http://localhost:8000/api/payment/verify/",
        }

        response = requests.post(f"{settings.PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
        res_data = response.json()

        if response.status_code != 200:
            return Response({"error": res_data.get("message", "Payment initialization failed.")}, status=400)

        reference = res_data['data']['reference']

        # Save Payment record
        Payment.objects.create(
            user=request.user,
            order=order,
            amount=order.total_amount,
            reference=reference
        )

        # Store reference in Order for easy linking
        order.payment_reference = reference
        order.save()

        return Response({
            "authorization_url": res_data['data']['authorization_url'],
            "access_code": res_data['data']['access_code'],
            "reference": reference
        }, status=status.HTTP_200_OK)


# ---- Verify Paystack Payment ----
class VerifyPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"error": "Reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        response = requests.get(f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
        res_data = response.json()

        if response.status_code != 200 or res_data['data']['status'] != 'success':
            return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark payment as verified
        try:
            payment = Payment.objects.get(reference=reference)
            payment.verified = True
            payment.save()

            # Update order status
            order = payment.order
            order.payment_status = 'paid'
            order.transaction_date = timezone.now()
            order.save()

        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)
