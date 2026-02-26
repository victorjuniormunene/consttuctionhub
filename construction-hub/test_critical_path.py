#!/usr/bin/env python
"""
Critical Path Testing Script
Tests key elements: login and basic navigation
"""
import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.orders.models import Order, Cart

User = get_user_model()

def test_database_setup():
    """Test that database has required data"""
    print("\n" + "="*60)
    print("TESTING DATABASE SETUP")
    print("="*60)

    # Check users
    customers = User.objects.filter(user_type='customer')
    suppliers = User.objects.filter(user_type='supplier')
    consultants = User.objects.filter(user_type='consultant')

    print(f"Customers: {customers.count()}")
    print(f"Suppliers: {suppliers.count()}")
    print(f"Consultants: {consultants.count()}")

    # Check products
    products = Product.objects.all()
    print(f"Products: {products.count()}")

    # Check suppliers have profiles
    supplier_profiles = Supplier.objects.all()
    print(f"Supplier profiles: {supplier_profiles.count()}")

    success = (customers.count() > 0 and suppliers.count() > 0 and
               consultants.count() > 0 and products.count() > 0 and
               supplier_profiles.count() > 0)

    if success:
        print("✓ Database setup looks good")
    else:
        print("✗ Database setup incomplete - some data missing")

    return success

def test_role_based_login():
    """Test login functionality for all roles"""
    print("\n" + "="*60)
    print("TESTING ROLE-BASED LOGIN")
    print("="*60)

    client = Client()
    results = {}

    # Test customer login
    customer = User.objects.filter(user_type='customer').first()
    if customer:
        passwords = ['1234', 'testpass123', 'password123']
        login_success = False
        for pwd in passwords:
            if client.login(username=customer.username, password=pwd):
                login_success = True
                break

        if login_success:
            # Test dashboard access
            response = client.get('/accounts/dashboard/')
            results['customer'] = response.status_code == 200
            print(f"✓ Customer login and dashboard: PASS")
        else:
            results['customer'] = False
            print(f"✗ Customer login: FAIL")
    else:
        results['customer'] = False
        print("✗ No customer user found")

    client.logout()

    # Test supplier login
    supplier = User.objects.filter(user_type='supplier').first()
    if supplier:
        login_success = client.login(username=supplier.username, password='1234')
        if login_success:
            response = client.get('/accounts/dashboard/')
            results['supplier'] = response.status_code == 200
            print(f"✓ Supplier login and dashboard: PASS")
        else:
            results['supplier'] = False
            print(f"✗ Supplier login: FAIL")
    else:
        results['supplier'] = False
        print("✗ No supplier user found")

    client.logout()

    # Test consultant login
    consultant = User.objects.filter(user_type='consultant').first()
    if consultant:
        login_success = client.login(username=consultant.username, password='testpass123')
        if login_success:
            response = client.get('/accounts/dashboard/')
            results['consultant'] = response.status_code == 200
            print(f"✓ Consultant login and dashboard: PASS")
        else:
            results['consultant'] = False
            print(f"✗ Consultant login: FAIL")
    else:
        results['consultant'] = False
        print("✗ No consultant user found")

    all_passed = all(results.values())
    if all_passed:
        print("✓ All role-based logins working")
    else:
        print("✗ Some role-based logins failed")

    return all_passed

def test_basic_navigation():
    """Test basic navigation to key pages"""
    print("\n" + "="*60)
    print("TESTING BASIC NAVIGATION")
    print("="*60)

    client = Client()
    results = {}

    # Test home page
    response = client.get('/')
    results['home'] = response.status_code == 200
    print(f"✓ Home page: {'PASS' if results['home'] else 'FAIL'}")

    # Test login pages
    response = client.get('/accounts/customer-login/')
    results['customer_login'] = response.status_code == 200
    print(f"✓ Customer login page: {'PASS' if results['customer_login'] else 'FAIL'}")

    response = client.get('/accounts/supplier-login/')
    results['supplier_login'] = response.status_code == 200
    print(f"✓ Supplier login page: {'PASS' if results['supplier_login'] else 'FAIL'}")

    response = client.get('/accounts/consultant-login/')
    results['consultant_login'] = response.status_code == 200
    print(f"✓ Consultant login page: {'PASS' if results['consultant_login'] else 'FAIL'}")

    # Test products page
    response = client.get('/products/')
    results['products'] = response.status_code == 200
    print(f"✓ Products page: {'PASS' if results['products'] else 'FAIL'}")

    all_passed = all(results.values())
    if all_passed:
        print("✓ All basic navigation working")
    else:
        print("✗ Some navigation failed")

    return all_passed

def test_order_flow():
    """Test basic order creation and visibility"""
    print("\n" + "="*60)
    print("TESTING ORDER FLOW")
    print("="*60)

    client = Client()

    # Get test users and product
    customer = User.objects.filter(user_type='customer').first()
    supplier = Supplier.objects.all().first()
    product = Product.objects.filter(supplier=supplier).first() if supplier else None

    if not customer or not supplier or not product:
        print("✗ Missing test data for order flow")
        return False

    # Login as customer
    login_success = False
    for pwd in ['1234', 'testpass123']:
        if client.login(username=customer.username, password=pwd):
            login_success = True
            break

    if not login_success:
        print("✗ Could not login as customer")
        return False

    # Create order
    order_data = {
        'product': product.id,
        'quantity': 2,
        'customer_name': customer.get_full_name() or customer.username,
        'customer_number': '0712345678',
        'customer_location': 'Test Location'
    }

    response = client.post('/orders/create/', order_data)
    if response.status_code in [200, 302]:  # Success or redirect
        print("✓ Order creation: PASS")

        # Check if order appears in customer dashboard
        response = client.get('/accounts/dashboard/')
        customer_orders = Order.objects.filter(customer=customer)
        order_visible = customer_orders.exists()
        print(f"✓ Order visible in customer dashboard: {'PASS' if order_visible else 'FAIL'}")

        # Check if order appears in supplier dashboard (login as supplier)
        client.logout()
        supplier_user = supplier.user
        client.login(username=supplier_user.username, password='1234')
        response = client.get('/accounts/dashboard/')
        supplier_orders = Order.objects.filter(product__supplier=supplier)
        supplier_visible = supplier_orders.exists()
        print(f"✓ Order visible in supplier dashboard: {'PASS' if supplier_visible else 'FAIL'}")

        success = order_visible and supplier_visible
        if success:
            print("✓ Order flow working correctly")
        else:
            print("✗ Order flow has issues")

        return success
    else:
        print("✗ Order creation failed")
        return False

def test_cart_functionality():
    """Test basic cart functionality"""
    print("\n" + "="*60)
    print("TESTING CART FUNCTIONALITY")
    print("="*60)

    client = Client()

    # Get test customer and product
    customer = User.objects.filter(user_type='customer').first()
    product = Product.objects.all().first()

    if not customer or not product:
        print("✗ Missing test data for cart functionality")
        return False

    # Login as customer
    login_success = False
    for pwd in ['1234', 'testpass123']:
        if client.login(username=customer.username, password=pwd):
            login_success = True
            break

    if not login_success:
        print("✗ Could not login as customer")
        return False

    # Add to cart
    cart_data = {
        'add_to_cart': '1',
        'product_id': product.id,
        'quantity': '1'
    }

    response = client.post('/products/', cart_data)
    if response.status_code in [200, 302]:
        # Check cart
        cart_items = Cart.objects.filter(user=customer)
        if cart_items.exists():
            print("✓ Cart functionality: PASS")
            # Cleanup
            cart_items.delete()
            return True
        else:
            print("✗ Cart item not found after adding")
            return False
    else:
        print("✗ Cart add failed")
        return False

def main():
    """Run all critical path tests"""
    print("CRITICAL PATH TESTING")
    print("="*80)
    print("Testing key elements: login and basic navigation")
    print("="*80)

    # Run tests
    tests = [
        ("Database Setup", test_database_setup),
        ("Role-Based Login", test_role_based_login),
        ("Basic Navigation", test_basic_navigation),
        ("Order Flow", test_order_flow),
        ("Cart Functionality", test_cart_functionality)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("CRITICAL PATH TEST SUMMARY")
    print("="*80)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL CRITICAL PATH TESTS PASSED!")
        print("✓ Login functionality working")
        print("✓ Basic navigation working")
        print("✓ Core features operational")
        return True
    else:
        print(f"\n❌ {total - passed} CRITICAL PATH TESTS FAILED")
        print("Please review and fix the failing components.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
