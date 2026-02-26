#!/usr/bin/env python
"""
Test script to verify that order status changes to 'completed' when M-Pesa message is pasted.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.orders.views import manual_mpesa_update
from apps.orders.models import Order
from apps.products.models import Product
from apps.suppliers.models import Supplier

def test_order_status_update():
    """Test that order status changes to 'completed' when valid M-Pesa message is pasted"""
    print("Testing order status update via M-Pesa message pasting...")

    # Create test data
    User = get_user_model()

    # Create supplier user
    supplier_user = User.objects.create_user(
        username='test_supplier',
        email='supplier@test.com',
        password='testpass123',
        user_type='supplier'
    )

    # Create supplier
    supplier = Supplier.objects.create(
        user=supplier_user,
        company_name='Test Supplier',
        contact_number='0712345678',
        location='Nairobi'
    )

    # Create product
    product = Product.objects.create(
        name='Test Product',
        description='Test product for order status testing',
        cost=100.00,
        available_quantity=10,
        supplier=supplier,
        category='materials'
    )

    # Create customer user
    customer_user = User.objects.create_user(
        username='test_customer',
        email='customer@test.com',
        password='testpass123',
        user_type='customer'
    )

    # Create order
    order = Order.objects.create(
        customer=customer_user,
        product=product,
        quantity=2,
        price=100.00,
        status='pending_payment',
        customer_name='Test Customer',
        customer_number='0712345678',
        customer_location='Nairobi'
    )

    print(f"Created order {order.order_number} with status: {order.status}")

    # Test M-Pesa message parsing
    factory = RequestFactory()
    mpesa_message = "UBB7G6CRBZ Confirmed. KSH200.00 sent to Daraja-Sandbox for account Order-ORD-00000387 on 11/2/26 at 4:12 PM New M-PESA balance is KSH0.37. Transaction cost, KSH0.00.Amount you can transact within the day is 499,980.00. Save frequent paybills for quick payment on M-PESA app https://bit.ly/mpesalnk"

    # Modify the message to match our order number
    mpesa_message = mpesa_message.replace("ORD-00000387", order.order_number)

    request = factory.post('/orders/manual-mpesa-update/', {
        'mpesa_message': mpesa_message
    })
    request.user = customer_user

    # Call the view
    response = manual_mpesa_update(request)

    # Refresh order from database
    order.refresh_from_db()

    print(f"Order status after M-Pesa update: {order.status}")
    print(f"Order payment status: {order.payment_status}")
    print(f"Order transaction ID: {order.mpesa_transaction_id}")

    # Verify the order status changed to 'completed'
    assert order.status == 'completed', f"Expected status 'completed', got '{order.status}'"
    assert order.payment_status == 'completed', f"Expected payment_status 'completed', got '{order.payment_status}'"
    assert order.mpesa_transaction_id == 'UBB7G6CRBZ', f"Expected transaction ID 'UBB7G6CRBZ', got '{order.mpesa_transaction_id}'"

    print("✅ Order status update test PASSED!")

    # Clean up
    order.delete()
    product.delete()
    supplier.delete()
    supplier_user.delete()
    customer_user.delete()

    print("Test completed successfully!")

if __name__ == '__main__':
    test_order_status_update()
