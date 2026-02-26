#!/usr/bin/env python
"""
Test script to verify M-Pesa STK push with updated BUSINESS_SHORTCODE
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.mpesa_utils import initiate_mpesa_payment_for_amount

def test_stk_push():
    """Test STK push payment initiation"""
    try:
        # Test parameters
        phone_number = '254708374149'  # M-Pesa test phone number
        amount = 1  # Small amount for testing
        reference = 'Test-STK-Push'

        print(f"Testing STK push with phone: {phone_number}, amount: {amount}, reference: {reference}")

        result = initiate_mpesa_payment_for_amount(amount, phone_number, reference)

        print(f"STK Push Result: {result}")

        if result.get('success'):
            print("✅ SUCCESS: STK push initiated successfully!")
            print(f"Checkout Request ID: {result.get('checkout_request_id')}")
            print(f"Response Code: {result.get('response_code')}")
            print(f"Customer Message: {result.get('customer_message')}")
            return True
        else:
            print("❌ FAILED: STK push failed")
            print(f"Error: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stk_push()

    if success:
        print("\n🎉 STK push test passed! The BUSINESS_SHORTCODE issue is fixed.")
    else:
        print("\n💥 STK push test failed. Check the error details above.")
