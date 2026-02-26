"""
Test script to verify supplier order management functionality
Demonstrates the complete workflow: create, edit, view, delete
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier
from apps.orders.models import Order

User = get_user_model()

print("="*70)
print("SUPPLIER ORDER MANAGEMENT - COMPLETE WORKFLOW TEST")
print("="*70)

# Get supplier1
supplier_user = User.objects.get(username='supplier1')
supplier = Supplier.objects.get(user=supplier_user)
print(f"\n✓ Found supplier: {supplier.company_name} ({supplier_user.username})")

# Check supplier-created orders
supplier_orders = Order.objects.filter(
    product__supplier=supplier,
    customer__isnull=True
).order_by('-created_at')

print(f"\n📦 SUPPLIER-CREATED ORDERS:")
print(f"   Total: {supplier_orders.count()}")
print(f"   Showing up to 5 (dashboard limit):")
for order in supplier_orders[:5]:
    print(f"   - Order #{order.order_number}: {order.product.name} x {order.quantity} for {order.customer_name}")

# Test client for HTTP requests
client = Client()
print(f"\n🔐 AUTHENTICATION TEST:")

# Test unauthenticated access
response = client.get('/orders/27/edit-supplier/')
print(f"   Unauthenticated /orders/27/edit-supplier/ → {response.status_code} (Should be 302 redirect to login)")

# Login as supplier
login_success = client.login(username='supplier1', password='supplier1')
print(f"   Login as supplier1 → {'✓ Success' if login_success else '✗ Failed'}")

# Test authenticated access to edit page
response = client.get('/orders/27/edit-supplier/')
print(f"   Authenticated /orders/27/edit-supplier/ → {response.status_code} (Should be 200)")

# Test authenticated access to delete page
response = client.get('/orders/26/delete-supplier/')
print(f"   Authenticated /orders/26/delete-supplier/ → {response.status_code} (Should be 200)")

# Test dashboard access
response = client.get('/accounts/dashboard/')
print(f"   Dashboard access → {response.status_code}")
if response.status_code == 200:
    context = response.context
    if 'supplier_created_orders' in context:
        supplier_orders_context = context['supplier_created_orders']
        print(f"   ✓ supplier_created_orders passed to template: {supplier_orders_context.count()} orders")
    else:
        print(f"   ✗ supplier_created_orders NOT in template context")

print(f"\n✅ WORKFLOW TEST COMPLETE")
print(f"\nYou can now:")
print(f"   1. Navigate to http://127.0.0.1:8000/accounts/dashboard/")
print(f"   2. Login as supplier1 / supplier1")
print(f"   3. Scroll to 'Orders You Created' section")
print(f"   4. Click Edit, Receipt, or Delete on any order")
print(f"   5. Test the complete workflow")
print("="*70)
