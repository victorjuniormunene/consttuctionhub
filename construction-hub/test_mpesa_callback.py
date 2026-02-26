#!/usr/bin/env python
"""
Test script for M-Pesa callback functionality
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.orders.mpesa_utils import mpesa_service

def test_successful_payment_callback():
    """Test successful payment callback"""
    print("Testing M-Pesa callback for successful payment...")

    # Create a test order
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Customer'
        }
    )

    # Create a test order
    order = Order.objects.create(
        customer=user,
        order_number='TEST-001',
        quantity=1,
        price=100.00,
        status='pending_payment',
        payment_status='pending',
        mpesa_checkout_request_id='ws_CO_TEST_123456789',
        mpesa_phone_number='254712345678'
    )

    print(f"Created test order: {order.order_number} with status: {order.status}")

    # Simulate successful payment callback
    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": "ws_CO_TEST_123456789",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {
                            "Name": "Amount",
                            "Value": 100.00
                        },
                        {
                            "Name": "MpesaReceiptNumber",
                            "Value": "NLJ7RT61SV"
                        },
                        {
                            "Name": "Balance"
                        },
                        {
                            "Name": "TransactionDate",
                            "Value": 20191122063845
                        },
                        {
                            "Name": "PhoneNumber",
                            "Value": 254708374149
                        }
                    ]
                }
            }
        }
    }

    # Process the callback
    result = mpesa_service.process_callback(callback_data)

    print(f"Callback processing result: {result}")

    # Refresh order from database
    order.refresh_from_db()

    print(f"Order status after callback: {order.status}")
    print(f"Payment status after callback: {order.payment_status}")
    print(f"M-Pesa transaction ID: {order.mpesa_transaction_id}")
    print(f"Payment completed at: {order.payment_completed_at}")

    # Verify the order was updated correctly
    assert order.status == 'paid', f"Expected status 'paid', got '{order.status}'"
    assert order.payment_status == 'completed', f"Expected payment_status 'completed', got '{order.payment_status}'"
    assert order.mpesa_transaction_id == 'NLJ7RT61SV', f"Expected transaction ID 'NLJ7RT61SV', got '{order.mpesa_transaction_id}'"
    assert order.payment_completed_at is not None, "Payment completed timestamp should be set"

    print("✅ SUCCESS: Order status updated correctly after successful payment callback!")

    # Clean up
    order.delete()
    if created:
        user.delete()

def test_failed_payment_callback():
    """Test failed payment callback"""
    print("\nTesting M-Pesa callback for failed payment...")

    # Create a test order
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_customer_fail',
        defaults={
            'email': 'testfail@example.com',
            'first_name': 'Test',
            'last_name': 'Customer Fail'
        }
    )

    # Create a test order
    order = Order.objects.create(
        customer=user,
        order_number='TEST-FAIL-001',
        quantity=1,
        price=100.00,
        status='pending_payment',
        payment_status='pending',
        mpesa_checkout_request_id='ws_CO_TEST_FAIL_123456789',
        mpesa_phone_number='254712345678'
    )

    print(f"Created test order: {order.order_number} with status: {order.status}")

    # Simulate failed payment callback
    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-2",
                "CheckoutRequestID": "ws_CO_TEST_FAIL_123456789",
                "ResultCode": 1,
                "ResultDesc": "The balance is insufficient for the transaction."
            }
        }
    }

    # Process the callback
    result = mpesa_service.process_callback(callback_data)

    print(f"Callback processing result: {result}")

    # Refresh order from database
    order.refresh_from_db()

    print(f"Order status after callback: {order.status}")
    print(f"Payment status after callback: {order.payment_status}")

    # Verify the order was updated correctly
    assert order.status == 'pending_payment', f"Expected status 'pending_payment', got '{order.status}'"
    assert order.payment_status == 'failed', f"Expected payment_status 'failed', got '{order.payment_status}'"

    print("✅ SUCCESS: Order status updated correctly after failed payment callback!")

    # Clean up
    order.delete()
    if created:
        user.delete()

if __name__ == '__main__':
    try:
        test_successful_payment_callback()
        test_failed_payment_callback()
        print("\n🎉 All M-Pesa callback tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
