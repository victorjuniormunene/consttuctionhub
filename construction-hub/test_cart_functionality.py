#!/usr/bin/env python
"""
Test script to verify cart functionality
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.orders.models import Cart

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

User = get_user_model()

def test_cart_functionality():
    """Test adding products to cart"""
    print("Testing cart functionality...")

    # Create test client
    client = Client()

    # Create test user
    user = User.objects.create_user(
        username='test_customer',
        email='test@example.com',
        password='testpass123',
        user_type='customer'
    )

    # Create test supplier
    supplier = Supplier.objects.create(
        user=user,
        company_name='Test Supplier',
        location='Test Location',
        contact_number='0712345678'
    )

    # Create test product
    product = Product.objects.create(
        name='Test Cement',
        description='Test cement product',
        cost=500.00,
        supplier=supplier,
        available_quantity=100
    )

    # Login user
    client.login(username='test_customer', password='testpass123')

    # Test adding to cart
    print("Adding product to cart...")
    response = client.post(reverse('products:product_list'), {
        'add_to_cart': '1',
        'product_id': product.id,
        'quantity': '2'
    })

    print(f"Response status: {response.status_code}")
    print(f"Redirect URL: {response.url}")

    # Check if item was added to cart
    cart_items = Cart.objects.filter(user=user)
    print(f"Cart items count: {cart_items.count()}")

    if cart_items.exists():
        cart_item = cart_items.first()
        print(f"Product: {cart_item.product.name}")
        print(f"Quantity: {cart_item.quantity}")
        print("✓ Cart functionality working!")
    else:
        print("✗ Cart functionality failed!")

    # Test adding another product
    product2 = Product.objects.create(
        name='Test Sand',
        description='Test sand product',
        cost=300.00,
        supplier=supplier,
        available_quantity=50
    )

    print("\nAdding second product to cart...")
    response2 = client.post(reverse('products:product_list'), {
        'add_to_cart': '1',
        'product_id': product2.id,
        'quantity': '1'
    })

    cart_items = Cart.objects.filter(user=user)
    print(f"Cart items count after second add: {cart_items.count()}")

    total_quantity = sum(item.quantity for item in cart_items)
    print(f"Total items in cart: {total_quantity}")

    # Test cart view
    print("\nTesting cart view...")
    response3 = client.get(reverse('products:cart'))
    print(f"Cart view status: {response3.status_code}")

    # Cleanup
    Cart.objects.filter(user=user).delete()
    product.delete()
    product2.delete()
    supplier.delete()
    user.delete()

    print("\n✓ All cart tests completed!")

if __name__ == '__main__':
    test_cart_functionality()
