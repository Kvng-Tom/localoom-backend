# payments/urls.py
from django.urls import path
from .views import InitializePaymentView, PaystackWebhookView, VerifyPaymentView

urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path("payment/webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),
]
