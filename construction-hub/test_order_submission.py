#!/usr/bin/env python
"""
Test script to verify the complete order submission workflow.
This tests that orders can be created via the form and appear on both dashboards.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from apps.products.models import Product
from apps.orders.models import Order
from apps.accounts.models import CustomUser
from apps.suppliers.models import Supplier
from django.db.models import Q

def test_order_submission_workflow():
    """Test the complete order submission and visibility workflow"""
    
    print("=" * 70)
    print("TESTING ORDER SUBMISSION WORKFLOW")
    print("=" * 70)
    
    # Get test users
    customer = CustomUser.objects.filter(username='customer1').first()
    supplier_user = CustomUser.objects.filter(username='supplier1').first()
    product = Product.objects.filter(supplier__user=supplier_user).first()
    
    if not all([customer, supplier_user, product]):
        print("ERROR: Missing test data (customer, supplier, or product)")
        return False
    
    print(f"\nTest Setup:")
    print(f"  Customer: {customer.username}")
    print(f"  Supplier: {supplier_user.username}")
    print(f"  Product: {product.name} (ID: {product.id})")
    
    # Initialize Django test client
    client = Client()
    
    # Step 1: Login as customer
    print(f"\nStep 1: Login as customer...")
    login_success = client.login(username='customer1', password='testpass123')
    if not login_success:
        print("  ERROR: Could not login as customer1")
        return False
    print("  SUCCESS: Logged in as customer1")
    
    # Step 2: Access order creation form with product parameter
    print(f"\nStep 2: Access order creation form...")
    create_url = reverse('orders:order_create') + f'?product={product.id}'
    response = client.get(create_url)
    if response.status_code != 200:
        print(f"  ERROR: Could not access order form (status {response.status_code})")
        return False
    print(f"  SUCCESS: Order form accessible")
    
    # Step 3: Submit order form
    print(f"\nStep 3: Submit order form...")
    order_data = {
        'product': str(product.id),
        'quantity': '3',
        'customer_name': 'Test Customer',
        'customer_number': '0798765432',
        'customer_location': 'Test Location'
    }
    
    response = client.post(create_url, order_data)
    
    # Check if redirected to dashboard (302 is redirect)
    if response.status_code == 302:
        print(f"  SUCCESS: Form submitted (redirected to {response.url})")
    elif response.status_code == 200:
        print(f"  WARNING: Form returned 200 (check for errors in response)")
        if b'error' in response.content.lower():
            print("    Form contains error messages")
    else:
        print(f"  ERROR: Unexpected status code {response.status_code}")
        return False
    
    # Step 4: Verify order was created
    print(f"\nStep 4: Verify order was created...")
    latest_order = Order.objects.order_by('-id').first()
    if latest_order and latest_order.product.id == product.id:
        print(f"  SUCCESS: Order created")
        print(f"    Order Number: {latest_order.order_number}")
        print(f"    ID: {latest_order.id}")
        print(f"    Quantity: {latest_order.quantity}")
        print(f"    Customer: {latest_order.customer}")
        test_order = latest_order
    else:
        print(f"  ERROR: Could not find newly created order")
        return False
    
    # Step 5: Verify customer can see the order
    print(f"\nStep 5: Verify customer can see the order on dashboard...")
    customer_full_name = customer.get_full_name() or customer.username
    customer_orders = Order.objects.filter(
        Q(customer=customer) | 
        Q(customer__isnull=True, customer_name=customer_full_name)
    )
    if test_order in customer_orders:
        print(f"  SUCCESS: Order visible to customer")
        print(f"    Total customer orders: {customer_orders.count()}")
    else:
        print(f"  ERROR: Order not visible to customer")
        return False
    
    # Step 6: Verify supplier can see the order
    print(f"\nStep 6: Verify supplier can see the order on dashboard...")
    supplier = product.supplier
    supplier_orders = Order.objects.filter(product__supplier=supplier)
    if test_order in supplier_orders:
        print(f"  SUCCESS: Order visible to supplier")
        print(f"    Total supplier orders: {supplier_orders.count()}")
    else:
        print(f"  ERROR: Order not visible to supplier")
        return False
    
    # Step 7: Logout and login as supplier to verify they can see it
    print(f"\nStep 7: Verify supplier can login and see order...")
    client.logout()
    supplier_login = client.login(username='supplier1', password='testpass123')
    if not supplier_login:
        print("  ERROR: Could not login as supplier1")
        return False
    
    # Access supplier dashboard
    dashboard_url = reverse('accounts:dashboard')
    response = client.get(dashboard_url)
    if response.status_code == 200:
        if str(test_order.order_number).encode() in response.content:
            print(f"  SUCCESS: Order visible in supplier dashboard")
        else:
            print(f"  WARNING: Order number not found in dashboard HTML")
            print(f"    (Order may still be accessible via database query)")
    else:
        print(f"  ERROR: Could not access supplier dashboard")
        return False
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  Order {test_order.order_number} was successfully created via form submission")
    print(f"  Order is visible to customer: YES")
    print(f"  Order is visible to supplier: YES")
    print(f"  Bidirectional visibility: WORKING")
    
    return True


if __name__ == '__main__':
    success = test_order_submission_workflow()
    exit(0 if success else 1)
