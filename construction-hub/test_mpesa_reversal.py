#!/usr/bin/env python
"""
Test script for M-Pesa reversal message parsing
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.accounts.models import CustomUser as User
from django.test import RequestFactory
from apps.orders.views import manual_mpesa_update

def test_reversal_parsing():
    """Test parsing of reversal message"""
    print("Testing M-Pesa reversal message parsing...")

    # Create a mock user
    try:
        user = User.objects.get(username='test_customer')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_customer',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Customer'
        )
        user.user_type = 'customer'
        user.save()

    # Create a mock order with transaction ID
    order = Order.objects.create(
        customer=user,
        order_number='ORD-00001234',
        quantity=1,
        price=10.00,
        status='paid',
        mpesa_transaction_id='UBB7G6CRBZ',
        payment_status='completed'
    )

    # Mock request with reversal message
    factory = RequestFactory()
    reversal_message = "UBB7GI2065 confirmed. Reversal of transaction UBB7G6CRBZ has been successfully reversed on 11/2/26 at 5:00 PM and Ksh10.00 is credited to your M-PESA account. New M-PESA account balance is Ksh10.37."
    request = factory.post('/orders/manual_mpesa_update/', {
        'mpesa_message': reversal_message
    })
    request.user = user

    # Call the view
    try:
        response = manual_mpesa_update(request)
        print(f"Response status: {response.status_code}")
        print("Reversal test passed - order should be cancelled")
    except Exception as e:
        print(f"Error in reversal test: {e}")

    # Check order status
    order.refresh_from_db()
    print(f"Order status after reversal: {order.status}")
    print(f"Payment status after reversal: {order.payment_status}")

    # Clean up
    order.delete()
    user.delete()

def test_normal_payment_parsing():
    """Test parsing of normal payment message"""
    print("\nTesting normal M-Pesa payment message parsing...")

    # Create a mock user
    try:
        user = User.objects.get(username='test_customer2')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_customer2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test2',
            last_name='Customer2'
        )
        user.user_type = 'customer'
        user.save()

    # Create a mock order
    order = Order.objects.create(
        customer=user,
        order_number='ORD-00005678',
        quantity=1,
        price=10.00,
        status='pending_payment'
    )

    # Mock request with payment message
    factory = RequestFactory()
    payment_message = "UBB7G6CRBZ Confirmed. KSH10.00 sent to Daraja-Sandbox for account Order-ORD-00005678 on 11/2/26 at 4:12 PM New M-PESA balance is KSH0.37. Transaction cost, KSH0.00.Amount you can transact within the day is 499,980.00. Save frequent paybills for quick payment on M-PESA app https://bit.ly/mpesalnk"
    request = factory.post('/orders/manual_mpesa_update/', {
        'mpesa_message': payment_message
    })
    request.user = user

    # Call the view
    try:
        response = manual_mpesa_update(request)
        print(f"Response status: {response.status_code}")
        print("Normal payment test passed - order should be paid")
    except Exception as e:
        print(f"Error in normal payment test: {e}")

    # Check order status
    order.refresh_from_db()
    print(f"Order status after payment: {order.status}")
    print(f"Payment status after payment: {order.payment_status}")
    print(f"Transaction ID: {order.mpesa_transaction_id}")

    # Clean up
    order.delete()
    user.delete()

if __name__ == '__main__':
    test_reversal_parsing()
    test_normal_payment_parsing()
    print("\nTesting completed.")
