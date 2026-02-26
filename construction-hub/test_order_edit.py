#!/usr/bin/env python
"""
Test script to verify order edit functionality in supplier dashboard
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.products.models import Product
from apps.suppliers.models import Supplier

def test_order_edit_functionality():
    """Test that order edit form includes price field and saves correctly"""
    print("Testing Order Edit Functionality")
    print("=" * 50)

    # Create test client
    client = Client()

    # Get or create test user
    User = get_user_model()
    try:
        supplier_user = User.objects.get(username='supplier1')
        print("✓ Found existing supplier user")
    except User.DoesNotExist:
        print("✗ Supplier user not found, creating test data...")
        return False

    # Login
    client.login(username='supplier1', password='password123')
    print("✓ Logged in as supplier")

    # Get supplier's orders
    try:
        supplier = Supplier.objects.get(user=supplier_user)
        orders = Order.objects.filter(product__supplier=supplier)
        if not orders.exists():
            print("✗ No orders found for supplier")
            return False

        order = orders.first()
        print(f"✓ Found order: {order.order_number}")

    except Exception as e:
        print(f"✗ Error getting supplier orders: {e}")
        return False

    # Test GET request to edit form
    edit_url = reverse('orders:edit_supplier_order', kwargs={'order_id': order.id})
    response = client.get(edit_url)

    if response.status_code != 200:
        print(f"✗ GET edit form failed: {response.status_code}")
        return False

    # Check if price field is in the form
    if 'id_price' not in response.content.decode():
        print("✗ Price field not found in edit form")
        return False

    print("✓ Price field found in edit form")

    # Test POST request with updated price
    original_price = order.price
    new_price = original_price + 100 if original_price else 1500

    post_data = {
        'quantity': order.quantity,
        'price': str(new_price),
        'customer_name': order.customer_name,
        'customer_number': order.customer_number,
        'customer_location': order.customer_location,
        'status': order.status,
    }

    response = client.post(edit_url, post_data, follow=True)

    if response.status_code != 200:
        print(f"✗ POST edit failed: {response.status_code}")
        return False

    # Refresh order from database
    order.refresh_from_db()

    if order.price != new_price:
        print(f"✗ Price not updated: expected {new_price}, got {order.price}")
        return False

    print(f"✓ Price updated successfully: {original_price} -> {new_price}")

    # Check total cost calculation
    expected_total = new_price * order.quantity
    if order.total_cost != expected_total:
        print(f"✗ Total cost incorrect: expected {expected_total}, got {order.total_cost}")
        return False

    print(f"✓ Total cost calculated correctly: {order.total_cost}")

    print("\n✓ All tests passed! Order edit functionality working correctly.")
    return True

if __name__ == '__main__':
    success = test_order_edit_functionality()
    sys.exit(0 if success else 1)
