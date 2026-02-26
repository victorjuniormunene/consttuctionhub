#!/usr/bin/env python
"""
End-to-end test for the complete payment flow:
1. Customer creates order
2. Initiates M-Pesa payment
3. M-Pesa callback processes payment
4. Verify order status updates in both customer and supplier dashboards
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.orders.models import Order
from apps.suppliers.models import Product, Supplier
from apps.orders.mpesa_utils import mpesa_service

class EndToEndPaymentFlowTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test users
        User = get_user_model()

        # Create customer
        self.customer = User.objects.create_user(
            username='test_customer_e2e',
            email='customer@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Customer'
        )

        # Create supplier
        self.supplier_user = User.objects.create_user(
            username='test_supplier_e2e',
            email='supplier@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Supplier',
            is_supplier=True
        )

        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            company_name='Test Supplier Co.',
            contact_number='0712345678',
            location='Nairobi'
        )

        # Create product
        self.product = Product.objects.create(
            supplier=self.supplier,
            name='Test Product',
            description='Test product for E2E testing',
            cost=100.00,
            category='materials',
            quality='standard',
            location='Nairobi',
            available_quantity=100
        )

    def test_complete_payment_flow(self):
        """Test the complete payment flow from order creation to payment completion"""
        print("🧪 Testing End-to-End Payment Flow...")

        # Step 1: Customer logs in
        login_success = self.client.login(username='test_customer_e2e', password='testpass123')
        self.assertTrue(login_success, "Customer login failed")
        print("✅ Customer logged in successfully")

        # Step 2: Create order
        order_data = {
            'product': self.product.id,
            'quantity': 2,
            'customer_name': 'Test Customer',
            'customer_number': '0712345678',
            'customer_location': 'Nairobi',
            'delivery_address': 'Test Address',
            'special_instructions': 'Test order'
        }

        response = self.client.post(reverse('orders:create_order', kwargs={'product_id': self.product.id}), order_data)
        self.assertEqual(response.status_code, 302, "Order creation failed")  # Redirect after success

        # Get the created order
        order = Order.objects.filter(customer=self.customer, product=self.product).latest('created_at')
        self.assertIsNotNone(order, "Order was not created")
        print(f"✅ Order created: {order.order_number}")

        # Step 3: Initiate payment
        payment_data = {
            'phone_number': '254712345678'  # Test phone number
        }

        response = self.client.post(reverse('orders:initiate_payment', kwargs={'order_id': order.id}), payment_data)
        self.assertEqual(response.status_code, 302, "Payment initiation failed")

        # Refresh order from database
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending_payment', "Order status should be pending_payment")
        self.assertEqual(order.payment_status, 'pending', "Payment status should be pending")
        self.assertIsNotNone(order.mpesa_checkout_request_id, "Checkout request ID should be set")
        print("✅ Payment initiated successfully")

        # Step 4: Simulate M-Pesa callback (successful payment)
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-123",
                    "CheckoutRequestID": order.mpesa_checkout_request_id,
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {
                                "Name": "Amount",
                                "Value": order.total_cost
                            },
                            {
                                "Name": "MpesaReceiptNumber",
                                "Value": "TEST123456789"
                            },
                            {
                                "Name": "TransactionDate",
                                "Value": 20240210123000
                            },
                            {
                                "Name": "PhoneNumber",
                                "Value": 254712345678
                            }
                        ]
                    }
                }
            }
        }

        # Process callback
        result = mpesa_service.process_callback(callback_data)
        self.assertTrue(result.get('success'), f"Callback processing failed: {result}")

        # Refresh order and verify status update
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid', "Order status should be 'paid' after successful payment")
        self.assertEqual(order.payment_status, 'completed', "Payment status should be 'completed'")
        self.assertEqual(order.mpesa_transaction_id, 'TEST123456789', "Transaction ID should be set")
        self.assertIsNotNone(order.payment_completed_at, "Payment completed timestamp should be set")
        print("✅ M-Pesa callback processed successfully - Order status updated to 'paid'")

        # Step 5: Verify customer dashboard shows updated order
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200, "Customer dashboard access failed")

        # Check if order appears in dashboard with correct status
        orders_in_dashboard = response.context['orders']
        order_in_dashboard = next((o for o in orders_in_dashboard if o.id == order.id), None)
        self.assertIsNotNone(order_in_dashboard, "Order should appear in customer dashboard")
        self.assertEqual(order_in_dashboard.status, 'paid', "Order should show 'paid' status in customer dashboard")
        print("✅ Customer dashboard reflects 'paid' status correctly")

        # Step 6: Verify supplier dashboard shows the order
        # Logout customer and login as supplier
        self.client.logout()
        supplier_login = self.client.login(username='test_supplier_e2e', password='testpass123')
        self.assertTrue(supplier_login, "Supplier login failed")

        response = self.client.get(reverse('dashboard:supplier_dashboard'))
        self.assertEqual(response.status_code, 200, "Supplier dashboard access failed")

        # Check if order appears in supplier's incoming orders
        supplier_orders = response.context['supplier_orders']
        order_in_supplier_dashboard = next((o for o in supplier_orders if o.id == order.id), None)
        self.assertIsNotNone(order_in_supplier_dashboard, "Order should appear in supplier dashboard")
        self.assertEqual(order_in_supplier_dashboard.status, 'paid', "Order should show 'paid' status in supplier dashboard")
        print("✅ Supplier dashboard shows order with 'paid' status")

        print("🎉 End-to-End Payment Flow Test PASSED!")

    def test_failed_payment_callback(self):
        """Test failed payment callback"""
        print("\n🧪 Testing Failed Payment Callback...")

        # Create order and initiate payment (similar to above)
        self.client.login(username='test_customer_e2e', password='testpass123')

        order_data = {
            'product': self.product.id,
            'quantity': 1,
            'customer_name': 'Test Customer',
            'customer_number': '0712345678',
            'customer_location': 'Nairobi'
        }

        self.client.post(reverse('orders:create_order', kwargs={'product_id': self.product.id}), order_data)
        order = Order.objects.filter(customer=self.customer).latest('created_at')

        payment_data = {'phone_number': '254712345678'}
        self.client.post(reverse('orders:initiate_payment', kwargs={'order_id': order.id}), payment_data)

        # Simulate failed payment callback
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-fail-123",
                    "CheckoutRequestID": order.mpesa_checkout_request_id,
                    "ResultCode": 1,
                    "ResultDesc": "Insufficient balance"
                }
            }
        }

        result = mpesa_service.process_callback(callback_data)
        self.assertTrue(result.get('success'), "Callback processing should succeed even for failures")

        # Verify order status remains pending_payment and payment_status is failed
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending_payment', "Order status should remain 'pending_payment'")
        self.assertEqual(order.payment_status, 'failed', "Payment status should be 'failed'")
        print("✅ Failed payment callback handled correctly")

    def tearDown(self):
        """Clean up test data"""
        Order.objects.filter(customer=self.customer).delete()
        Product.objects.filter(supplier=self.supplier).delete()
        Supplier.objects.filter(user=self.supplier_user).delete()
        self.customer.delete()
        self.supplier_user.delete()

if __name__ == '__main__':
    # Run the tests
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(EndToEndPaymentFlowTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n🎉 All End-to-End Payment Flow Tests PASSED!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        sys.exit(1)
