#!/usr/bin/env python
"""
Test script to verify the M-Pesa callback fix for bulk payments
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.orders.mpesa_utils import mpesa_service
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.suppliers.models import Supplier

def test_callback_processing():
    """Test that callback processing works for multiple orders with same checkout_request_id"""
    print("Testing M-Pesa callback processing for bulk payments...")

    # Create test data
    User = get_user_model()

    # Create a customer
    customer = User.objects.create_user(
        username='test_customer',
        email='customer@test.com',
        password='testpass123',
        user_type='customer'
    )

    # Create a supplier
    supplier_user = User.objects.create_user(
        username='test_supplier',
        email='supplier@test.com',
        password='testpass123',
        user_type='supplier'
    )

    supplier = Supplier.objects.create(
        user=supplier_user,
        company_name='Test Supplier',
        contact_number='0712345678',
        location='Nairobi'
    )

    # Create a product
    product = Product.objects.create(
        name='Test Product',
        description='Test product for callback testing',
        cost=100.00,
        category='materials',
        supplier=supplier,
        available_quantity=10
    )

    # Create multiple orders with the same checkout_request_id (simulating bulk payment)
    checkout_request_id = 'test_checkout_123'

    orders = []
    for i in range(3):
        order = Order.objects.create(
            customer=customer,
            product=product,
            quantity=1,
            price=100.00,
            customer_name='Test Customer',
            customer_number='0712345678',
            customer_location='Nairobi',
            status='pending_payment',
            payment_status='pending',
            mpesa_checkout_request_id=checkout_request_id
        )
        orders.append(order)

    print(f"Created {len(orders)} test orders with checkout_request_id: {checkout_request_id}")

    # Simulate successful M-Pesa callback
    callback_data = {
        'Body': {
            'stkCallback': {
                'ResultCode': 0,  # Success
                'CheckoutRequestID': checkout_request_id,
                'CallbackMetadata': {
                    'Item': [
                        {'Name': 'MpesaReceiptNumber', 'Value': 'TEST123456'},
                        {'Name': 'PhoneNumber', 'Value': '254712345678'}
                    ]
                }
            }
        }
    }

    # Process the callback
    result = mpesa_service.process_callback(callback_data)

    print(f"Callback processing result: {result}")

    # Verify all orders were updated
    updated_orders = Order.objects.filter(mpesa_checkout_request_id=checkout_request_id)

    success_count = 0
    for order in updated_orders:
        if order.status == 'paid' and order.payment_status == 'completed':
            success_count += 1
            print(f"✅ Order {order.order_number}: status={order.status}, payment_status={order.payment_status}")
        else:
            print(f"❌ Order {order.order_number}: status={order.status}, payment_status={order.payment_status}")

    print(f"\nSummary: {success_count}/{len(orders)} orders updated successfully")

    # Cleanup
    Order.objects.filter(mpesa_checkout_request_id=checkout_request_id).delete()
    product.delete()
    supplier.delete()
    supplier_user.delete()
    customer.delete()

    return success_count == len(orders)

if __name__ == '__main__':
    success = test_callback_processing()
    if success:
        print("\n🎉 Callback fix test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Callback fix test FAILED!")
        sys.exit(1)
