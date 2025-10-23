from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
   class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "user", "amount", "reference", "verified", "created_at", "order"
        ]

class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(required=True)

class InitializePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)

