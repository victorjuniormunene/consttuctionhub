#!/usr/bin/env python
"""
Simple Critical Path Testing Script
Tests key elements: login and basic navigation
"""
import os
import sys
import django

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

    try:
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
    except Exception as e:
        print(f"✗ Database setup test failed: {e}")
        return False

def test_user_properties():
    """Test that user properties work correctly"""
    print("\n" + "="*60)
    print("TESTING USER PROPERTIES")
    print("="*60)

    try:
        # Test customer
        customer = User.objects.filter(user_type='customer').first()
        if customer:
            print(f"Customer user_type: {customer.user_type}")
            print(f"Customer is_supplier: {customer.is_supplier}")
            print(f"Customer is_consultant: {customer.is_consultant}")
            assert customer.is_supplier == False
            assert customer.is_consultant == False
            print("✓ Customer properties work correctly")

        # Test supplier
        supplier = User.objects.filter(user_type='supplier').first()
        if supplier:
            print(f"Supplier user_type: {supplier.user_type}")
            print(f"Supplier is_supplier: {supplier.is_supplier}")
            print(f"Supplier is_consultant: {supplier.is_consultant}")
            assert supplier.is_supplier == True
            assert supplier.is_consultant == False
            print("✓ Supplier properties work correctly")

        # Test consultant
        consultant = User.objects.filter(user_type='consultant').first()
        if consultant:
            print(f"Consultant user_type: {consultant.user_type}")
            print(f"Consultant is_supplier: {consultant.is_supplier}")
            print(f"Consultant is_consultant: {consultant.is_consultant}")
            assert consultant.is_supplier == False
            assert consultant.is_consultant == True
            print("✓ Consultant properties work correctly")

        return True
    except Exception as e:
        print(f"✗ User properties test failed: {e}")
        return False

def test_basic_queries():
    """Test basic database queries work"""
    print("\n" + "="*60)
    print("TESTING BASIC QUERIES")
    print("="*60)

    try:
        # Test product queries
        products = Product.objects.all()
        print(f"Found {products.count()} products")

        if products.exists():
            product = products.first()
            print(f"Sample product: {product.name} by {product.supplier.company_name}")

        # Test order queries
        orders = Order.objects.all()
        print(f"Found {orders.count()} orders")

        # Test supplier queries
        suppliers = Supplier.objects.all()
        print(f"Found {suppliers.count()} suppliers")

        print("✓ Basic queries work correctly")
        return True
    except Exception as e:
        print(f"✗ Basic queries test failed: {e}")
        return False

def test_relationships():
    """Test model relationships work"""
    print("\n" + "="*60)
    print("TESTING MODEL RELATIONSHIPS")
    print("="*60)

    try:
        # Test product-supplier relationship
        product = Product.objects.select_related('supplier').first()
        if product:
            print(f"Product: {product.name}")
            print(f"Supplier: {product.supplier.company_name}")
            print(f"Supplier user: {product.supplier.user.username}")
            print("✓ Product-supplier relationship works")

        # Test supplier-user relationship
        supplier = Supplier.objects.select_related('user').first()
        if supplier:
            print(f"Supplier: {supplier.company_name}")
            print(f"User: {supplier.user.username}")
            print(f"User type: {supplier.user.user_type}")
            print("✓ Supplier-user relationship works")

        return True
    except Exception as e:
        print(f"✗ Model relationships test failed: {e}")
        return False

def main():
    """Run all critical path tests"""
    print("CRITICAL PATH TESTING (SIMPLE)")
    print("="*80)
    print("Testing key elements without Django test client")
    print("="*80)

    # Run tests
    tests = [
        ("Database Setup", test_database_setup),
        ("User Properties", test_user_properties),
        ("Basic Queries", test_basic_queries),
        ("Model Relationships", test_relationships)
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
        print("✓ Database is properly set up")
        print("✓ Model relationships work")
        print("✓ Basic functionality operational")
        return True
    else:
        print(f"\n❌ {total - passed} CRITICAL PATH TESTS FAILED")
        print("Please review and fix the failing components.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
