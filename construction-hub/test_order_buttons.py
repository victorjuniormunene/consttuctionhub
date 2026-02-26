"""
Test script to verify the 3 button functionality in My Orders page:
1. View Details - Opens order detail view
2. Complete Payment - Initiates payment for pending orders
3. Track Order - Opens tracking page
4. Message Supplier - Opens messaging with supplier

Run with: cd construction-hub && python manage.py shell < test_order_buttons.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.products.models import Product
from apps.suppliers.models import Supplier

User = get_user_model()

def test_order_buttons():
    print("=" * 60)
    print("Testing Order Buttons Functionality")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Try to get or create a test customer
    try:
        customer = User.objects.filter(user_type='customer').first()
        if not customer:
            print("\n❌ No customer user found. Creating one...")
            customer = User.objects.create_user(
                username='test_customer',
                email='test@example.com',
                password='testpass123',
                user_type='customer'
            )
            print(f"✓ Created test customer: {customer.username}")
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
        return
    
    # Login as customer
    logged_in = client.login(username=customer.username, password='testpass123')
    if not logged_in:
        print(f"\n❌ Failed to login as {customer.username}")
        return
    print(f"\n✓ Logged in as: {customer.username}")
    
    # Test 1: Order List View
    print("\n" + "-" * 40)
    print("TEST 1: Order List View")
    print("-" * 40)
    response = client.get('/orders/')
    if response.status_code == 200:
        print("✓ Order list page loads successfully")
        # Check if buttons are in the template
        content = response.content.decode('utf-8')
        if 'View Details' in content:
            print("✓ 'View Details' button found in template")
        else:
            print("❌ 'View Details' button NOT found in template")
        if 'Complete Payment' in content:
            print("✓ 'Complete Payment' button found in template")
        else:
            print("❌ 'Complete Payment' button NOT found in template")
        if 'Track Order' in content:
            print("✓ 'Track Order' button found in template")
        else:
            print("❌ 'Track Order' button NOT found in template")
        if 'Message Supplier' in content:
            print("✓ 'Message Supplier' button found in template")
        else:
            print("❌ 'Message Supplier' button NOT found in template")
    else:
        print(f"❌ Order list page failed to load: {response.status_code}")
    
    # Get an order to test with
    order = Order.objects.filter(customer=customer).first()
    if not order:
        print("\n❌ No orders found for this customer")
        # Check if there are any orders in the system
        total_orders = Order.objects.count()
        print(f"   Total orders in system: {total_orders}")
        
        # Try to find any customer order
        any_order = Order.objects.first()
        if any_order:
            print(f"   Sample order: {any_order.order_number} - Status: {any_order.status}")
    else:
        print(f"\n✓ Testing with order: {order.order_number}")
        print(f"   Status: {order.status}")
        
        # Test 2: View Details Button
        print("\n" + "-" * 40)
        print("TEST 2: View Details Button")
        print("-" * 40)
        # Check if order_detail URL is configured
        from django.urls import reverse
        try:
            detail_url = reverse('orders:order_detail', args=[order.id])
            print(f"✓ Order detail URL exists: {detail_url}")
            response = client.get(detail_url)
            if response.status_code == 200:
                print("✓ Order detail view works")
            elif response.status_code == 302:
                print("⚠ Order detail view redirects (may need login or is disabled)")
            else:
                print(f"❌ Order detail view failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Order detail URL not found: {e}")
        
        # Test 3: Complete Payment Button
        print("\n" + "-" * 40)
        print("TEST 3: Complete Payment Button")
        print("-" * 40)
        if order.status in ['saved', 'pending_payment']:
            try:
                payment_url = reverse('orders:payment', args=[order.id])
                print(f"✓ Payment URL: {payment_url}")
                response = client.get(payment_url)
                if response.status_code == 200:
                    print("✓ Payment page loads successfully")
                else:
                    print(f"❌ Payment page failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Payment URL error: {e}")
        else:
            print(f"⚠ Order status is '{order.status}', payment button not shown")
        
        # Test 4: Track Order Button
        print("\n" + "-" * 40)
        print("TEST 4: Track Order Button")
        print("-" * 40)
        try:
            tracking_url = reverse('orders:order_tracking', args=[order.id])
            print(f"✓ Tracking URL: {tracking_url}")
            response = client.get(tracking_url)
            if response.status_code == 200:
                print("✓ Order tracking page loads successfully")
            else:
                print(f"❌ Order tracking page failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Tracking URL error: {e}")
        
        # Test 5: Message Supplier Button
        print("\n" + "-" * 40)
        print("TEST 5: Message Supplier Button")
        print("-" * 40)
        
        # Check if order has a supplier
        if order.product and hasattr(order.product, 'supplier'):
            print(f"✓ Order has supplier: {order.product.supplier.company_name}")
            # Test the API endpoint
            try:
                api_url = reverse('messaging:api_create_conversation')
                print(f"✓ Messaging API URL: {api_url}")
                
                # Test POST to create conversation
                response = client.post(
                    api_url,
                    data={'order_id': order.id, 'message': 'Test message'},
                    content_type='application/json'
                )
                if response.status_code in [200, 201]:
                    print("✓ Message supplier API works")
                else:
                    print(f"⚠ Message supplier API returned: {response.status_code}")
                    print(f"   Response: {response.content.decode('utf-8')[:200]}")
            except Exception as e:
                print(f"❌ Messaging API error: {e}")
        else:
            print("⚠ Order has no supplier - Message Supplier button will show 'No Supplier'")

    # Test 6: Order Status API
    print("\n" + "-" * 40)
    print("TEST 6: Order Status API (for real-time tracking)")
    print("-" * 40)
    if order:
        try:
            api_url = f"/orders/api/orders/{order.id}/status/"
            response = client.get(api_url)
            if response.status_code == 200:
                print("✓ Order status API works")
            else:
                print(f"❌ Order status API failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Order status API error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("""
Buttons to test in the UI:
1. View Details - Opens order detail page
2. Complete Payment - Opens M-Pesa payment page (for pending orders)
3. Track Order - Opens order tracking page
4. Message Supplier - Opens chat with supplier (if supplier exists)

Notes:
- 'View Details' may show alert if order_detail view is not enabled
- 'No Supplier' shows when order has no associated supplier
- Payment button only shows for orders with status 'saved' or 'pending_payment'
""")

if __name__ == '__main__':
    test_order_buttons()
