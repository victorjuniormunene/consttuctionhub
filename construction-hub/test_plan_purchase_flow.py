#!/usr/bin/env python
import os
import django
import requests
from django.contrib.auth import get_user_model
from apps.orders.models import Order

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

User = get_user_model()

print("\n" + "="*80)
print("TESTING PLAN PURCHASE FLOW")
print("="*80)

# Get or create a test customer
try:
    customer = User.objects.get(username='test_customer')
except User.DoesNotExist:
    customer = User.objects.create_user(
        username='test_customer',
        email='test@example.com',
        password='testpass123',
        user_type='customer'
    )
    print("✓ Created test customer")

print(f"✓ Using customer: {customer.username}")

# Test 1: Purchase plan
print("\n📝 Test 1: Purchasing 2 bedroom plan...")
try:
    # Simulate the purchase_plan view
    from apps.accounts.views import purchase_plan
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.middleware import AuthenticationMiddleware

    factory = RequestFactory()
    request = factory.get('/accounts/purchase_plan/2_bedroom/')
    request.user = customer

    # Add session
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    response = purchase_plan(request, '2_bedroom')
    print(f"✓ Purchase response status: {response.status_code}")

    # Check if order was created
    orders = Order.objects.filter(customer=customer, plan_type='2_bedroom').order_by('-created_at')
    if orders.exists():
        order = orders.first()
        print(f"✓ Order created: #{order.id} ({order.order_number}) - Status: {order.status}")
    else:
        print("❌ No order created")
        exit(1)

except Exception as e:
    print(f"❌ Purchase failed: {e}")
    exit(1)

# Test 2: Check payment page
print("\n💳 Test 2: Accessing payment page...")
try:
    from apps.orders.views import payment

    request = factory.get(f'/orders/{order.id}/payment/')
    request.user = customer

    response = payment(request, order.id)
    print(f"✓ Payment page response status: {response.status_code}")

except Exception as e:
    print(f"❌ Payment page failed: {e}")
    exit(1)

# Test 3: Submit payment
print("\n✅ Test 3: Submitting payment...")
try:
    request = factory.post(f'/orders/{order.id}/payment/')
    request.user = customer

    response = payment(request, order.id)
    print(f"✓ Payment submission response status: {response.status_code}")

    # Refresh order from DB
    order.refresh_from_db()
    print(f"✓ Order status after payment: {order.status}")

    if order.status == 'paid':
        print("✅ Payment successful!")
    else:
        print("❌ Payment not marked as paid")
        exit(1)

except Exception as e:
    print(f"❌ Payment submission failed: {e}")
    exit(1)

# Test 4: Download plan
print("\n📥 Test 4: Downloading plan...")
try:
    from apps.orders.views import download_plan

    request = factory.get('/orders/download-plan/2_bedroom/')
    request.user = customer

    response = download_plan(request, '2_bedroom')
    print(f"✓ Download response status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Plan download successful!")
    else:
        print("❌ Plan download failed")
        exit(1)

except Exception as e:
    print(f"❌ Download failed: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED! Plan purchase flow works correctly.")
print("="*80 + "\n")
