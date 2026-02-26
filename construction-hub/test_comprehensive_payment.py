#!/usr/bin/env python
"""
Comprehensive test script for M-Pesa payment functionality
Tests all aspects of the payment system including callbacks, single/bulk payments, and error scenarios
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.orders.mpesa_utils import mpesa_service
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.suppliers.models import Supplier
from django.test import TestCase, Client
from django.urls import reverse

def setup_test_data():
    """Create test data for payment testing"""
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
        description='Test product for payment testing',
        cost=100.00,
        category='materials',
        supplier=supplier,
        available_quantity=10
    )

    return customer, supplier, product

def cleanup_test_data(customer, supplier, product):
    """Clean up test data"""
    Order.objects.filter(customer=customer).delete()
    product.delete()
    supplier.delete()
    supplier.user.delete()
    customer.delete()

def test_single_order_callback():
    """Test callback processing for single order payment"""
    print("\n🧪 Testing Single Order Callback Processing...")

    customer, supplier, product = setup_test_data()

    # Create single order
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
        mpesa_checkout_request_id='single_test_123'
    )

    # Simulate successful callback
    callback_data = {
        'Body': {
            'stkCallback': {
                'ResultCode': 0,
                'CheckoutRequestID': 'single_test_123',
                'CallbackMetadata': {
                    'Item': [
                        {'Name': 'MpesaReceiptNumber', 'Value': 'SINGLE123456'},
                        {'Name': 'PhoneNumber', 'Value': '254712345678'}
                    ]
                }
            }
        }
    }

    result = mpesa_service.process_callback(callback_data)

    # Verify results
    order.refresh_from_db()
    success = (
        result.get('success') == True and
        order.status == 'paid' and
        order.payment_status == 'completed' and
        order.mpesa_transaction_id == 'SINGLE123456'
    )

    cleanup_test_data(customer, supplier, product)

    if success:
        print("✅ Single order callback test PASSED")
        return True
    else:
        print("❌ Single order callback test FAILED")
        print(f"Result: {result}")
        print(f"Order status: {order.status}, payment_status: {order.payment_status}")
        return False

def test_bulk_order_callback():
    """Test callback processing for bulk order payment"""
    print("\n🧪 Testing Bulk Order Callback Processing...")

    customer, supplier, product = setup_test_data()

    # Create multiple orders with same checkout_request_id
    checkout_id = 'bulk_test_456'
    orders = []
    for i in range(3):
        order = Order.objects.create(
            customer=customer,
            product=product,
            quantity=1,
            price=100.00,
            customer_name=f'Test Customer {i}',
            customer_number='0712345678',
            customer_location='Nairobi',
            status='pending_payment',
            payment_status='pending',
            mpesa_checkout_request_id=checkout_id
        )
        orders.append(order)

    # Simulate successful bulk callback
    callback_data = {
        'Body': {
            'stkCallback': {
                'ResultCode': 0,
                'CheckoutRequestID': checkout_id,
                'CallbackMetadata': {
                    'Item': [
                        {'Name': 'MpesaReceiptNumber', 'Value': 'BULK789012'},
                        {'Name': 'PhoneNumber', 'Value': '254712345678'}
                    ]
                }
            }
        }
    }

    result = mpesa_service.process_callback(callback_data)

    # Verify all orders were updated
    success_count = 0
    for order in orders:
        order.refresh_from_db()
        if (order.status == 'paid' and
            order.payment_status == 'completed' and
            order.mpesa_transaction_id == 'BULK789012'):
            success_count += 1

    cleanup_test_data(customer, supplier, product)

    success = success_count == len(orders) and result.get('success') == True
    if success:
        print("✅ Bulk order callback test PASSED")
        return True
    else:
        print("❌ Bulk order callback test FAILED")
        print(f"Updated orders: {success_count}/{len(orders)}")
        print(f"Result: {result}")
        return False

def test_failed_payment_callback():
    """Test callback processing for failed payment"""
    print("\n🧪 Testing Failed Payment Callback Processing...")

    customer, supplier, product = setup_test_data()

    # Create order
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
        mpesa_checkout_request_id='failed_test_789'
    )

    # Simulate failed callback
    callback_data = {
        'Body': {
            'stkCallback': {
                'ResultCode': 1,  # Failure
                'ResultDesc': 'Insufficient funds',
                'CheckoutRequestID': 'failed_test_789'
            }
        }
    }

    result = mpesa_service.process_callback(callback_data)

    # Verify order status
    order.refresh_from_db()
    success = (
        result.get('success') == False and
        order.payment_status == 'failed' and
        order.status == 'pending_payment'  # Should remain pending
    )

    cleanup_test_data(customer, supplier, product)

    if success:
        print("✅ Failed payment callback test PASSED")
        return True
    else:
        print("❌ Failed payment callback test FAILED")
        print(f"Result: {result}")
        print(f"Order payment_status: {order.payment_status}, status: {order.status}")
        return False

def test_callback_endpoint():
    """Test the actual Django callback endpoint"""
    print("\n🧪 Testing M-Pesa Callback Endpoint...")

    customer, supplier, product = setup_test_data()

    # Create order
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
        mpesa_checkout_request_id='endpoint_test_999'
    )

    # Test with Django test client
    client = Client()

    callback_data = {
        'Body': {
            'stkCallback': {
                'ResultCode': 0,
                'CheckoutRequestID': 'endpoint_test_999',
                'CallbackMetadata': {
                    'Item': [
                        {'Name': 'MpesaReceiptNumber', 'Value': 'ENDPOINT111222'},
                        {'Name': 'PhoneNumber', 'Value': '254712345678'}
                    ]
                }
            }
        }
    }

    response = client.post(
        reverse('orders:mpesa_callback'),
        data=json.dumps(callback_data),
        content_type='application/json'
    )

    # Verify response
    order.refresh_from_db()
    success = (
        response.status_code == 200 and
        order.status == 'paid' and
        order.payment_status == 'completed' and
        order.mpesa_transaction_id == 'ENDPOINT111222'
    )

    cleanup_test_data(customer, supplier, product)

    if success:
        print("✅ Callback endpoint test PASSED")
        return True
    else:
        print("❌ Callback endpoint test FAILED")
        print(f"Response status: {response.status_code}")
        print(f"Order status: {order.status}, payment_status: {order.payment_status}")
        return False

def test_manual_mpesa_update():
    """Test manual M-Pesa message parsing and order update"""
    print("\n🧪 Testing Manual M-Pesa Message Update...")

    customer, supplier, product = setup_test_data()

    # Create order
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
        mpesa_checkout_request_id='manual_test_888',
        order_number='ORD-0000123'
    )

    # Simulate manual update via view
    client = Client()
    client.login(username='test_customer', password='testpass123')

    mpesa_message = "MANUAL123 Confirmed. KSH100.00 sent to Daraja-Sandbox for account Order-ORD-0000123 on 11/2/26 at 4:12 PM New M-PESA balance is KSH0.37. Transaction cost, KSH0.00.Amount you can transact within the day is 499,980.00. Save frequent paybills for quick payment on M-PESA app https://bit.ly/mpesalnk"

    # This would normally be done via POST to a manual update endpoint
    # For now, we'll test the parsing logic directly
    import re
    from datetime import datetime

    # Extract transaction ID
    transaction_id_match = re.search(r'^([A-Z0-9]+)\s+Confirmed', mpesa_message)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else None

    # Extract account reference
    account_match = re.search(r'for account\s+([^\s]+)', mpesa_message)
    account_reference = account_match.group(1) if account_match else None

    # Check if account reference matches order
    expected_reference = f"Order-{order.order_number}"
    reference_matches = account_reference == expected_reference

    # Manual update logic
    if transaction_id and reference_matches:
        order.payment_status = 'completed'
        order.mpesa_transaction_id = transaction_id
        order.status = 'paid'
        order.payment_completed_at = datetime.now()
        order.save()
        success = True
    else:
        success = False

    cleanup_test_data(customer, supplier, product)

    if success and order.status == 'paid':
        print("✅ Manual M-Pesa update test PASSED")
        return True
    else:
        print("❌ Manual M-Pesa update test FAILED")
        print(f"Transaction ID: {transaction_id}")
        print(f"Account reference: {account_reference}")
        print(f"Expected reference: {expected_reference}")
        print(f"Reference matches: {reference_matches}")
        return False

def run_all_tests():
    """Run all payment tests"""
    print("🚀 Starting Comprehensive M-Pesa Payment Tests")
    print("=" * 50)

    tests = [
        test_single_order_callback,
        test_bulk_order_callback,
        test_failed_payment_callback,
        test_callback_endpoint,
        test_manual_mpesa_update,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} CRASHED: {str(e)}")
            results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED!")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
