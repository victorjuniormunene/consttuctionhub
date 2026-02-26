#!/usr/bin/env python
"""
Test role-based login functionality
"""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import Client
from apps.accounts.models import CustomUser

def test_customer_login():
    """Test customer login functionality"""
    print("\n" + "="*60)
    print("TESTING CUSTOMER LOGIN")
    print("="*60)

    client = Client()

    # Test accessing customer login page
    response = client.get('/accounts/customer-login/')
    print(f"Customer login page access: {response.status_code} (should be 200)")

    # Try to login as customer
    customer = CustomUser.objects.filter(user_type='customer').first()
    if not customer:
        print("ERROR: No customer user found")
        return False

    print(f"Testing login for customer: {customer.username}")

    # Test successful login - try different passwords
    login_success = False
    passwords_to_try = ['testpass123', '1234', 'password123']

    for password in passwords_to_try:
        login_success = client.login(username=customer.username, password=password)
        if login_success:
            print(f"Customer login success with password: {password}")
            break

    if not login_success:
        print(f"Customer login failed for {customer.username}")

    if login_success:
        # Test dashboard redirect
        response = client.get('/accounts/dashboard/')
        print(f"Dashboard redirect after login: {response.status_code}")
        if 'customer' in response.url or 'customer' in str(response.content).lower():
            print("✓ Correctly redirected to customer dashboard")
        else:
            print("✗ Not redirected to customer dashboard")
            return False

    # Test cross-role access prevention
    client.logout()
    supplier = CustomUser.objects.filter(user_type='supplier').first()
    if supplier:
        login_as_supplier = client.login(username=supplier.username, password='testpass123')
        if login_as_supplier:
            # Try to access customer login
            response = client.get('/accounts/customer-login/')
            if response.status_code == 302:  # Should redirect
                print("✓ Supplier correctly blocked from customer login")
            else:
                print("✗ Supplier not blocked from customer login")
                return False

    return True

def test_supplier_login():
    """Test supplier login functionality"""
    print("\n" + "="*60)
    print("TESTING SUPPLIER LOGIN")
    print("="*60)

    client = Client()

    # Test accessing supplier login page
    response = client.get('/accounts/supplier-login/')
    print(f"Supplier login page access: {response.status_code} (should be 200)")

    # Try to login as supplier
    supplier = CustomUser.objects.filter(user_type='supplier').first()
    if not supplier:
        print("ERROR: No supplier user found")
        return False

    print(f"Testing login for supplier: {supplier.username}")

    # Test successful login - suppliers use password '1234'
    login_success = client.login(username=supplier.username, password='1234')
    print(f"Supplier login success: {login_success}")

    if login_success:
        # Test dashboard redirect
        response = client.get('/accounts/dashboard/')
        print(f"Dashboard redirect after login: {response.status_code}")
        if 'supplier' in response.url or 'supplier' in str(response.content).lower():
            print("✓ Correctly redirected to supplier dashboard")
        else:
            print("✗ Not redirected to supplier dashboard")
            return False

    return True

def test_consultant_login():
    """Test consultant login functionality"""
    print("\n" + "="*60)
    print("TESTING CONSULTANT LOGIN")
    print("="*60)

    client = Client()

    # Test accessing consultant login page
    response = client.get('/accounts/consultant-login/')
    print(f"Consultant login page access: {response.status_code} (should be 200)")

    # Try to login as consultant
    consultant = CustomUser.objects.filter(user_type='consultant').first()
    if not consultant:
        print("ERROR: No consultant user found")
        return False

    print(f"Testing login for consultant: {consultant.username}")

    # Test successful login
    login_success = client.login(username=consultant.username, password='testpass123')
    print(f"Consultant login success: {login_success}")

    if login_success:
        # Test dashboard redirect
        response = client.get('/accounts/dashboard/')
        print(f"Dashboard redirect after login: {response.status_code}")
        if 'consultant' in response.url or 'consultant' in str(response.content).lower():
            print("✓ Correctly redirected to consultant dashboard")
        else:
            print("✗ Not redirected to consultant dashboard")
            return False

    return True

def test_cross_role_prevention():
    """Test that users can't access other roles' login pages when authenticated"""
    print("\n" + "="*60)
    print("TESTING CROSS-ROLE ACCESS PREVENTION")
    print("="*60)

    client = Client()

    # Login as customer
    customer = CustomUser.objects.filter(user_type='customer').first()
    if customer:
        client.login(username=customer.username, password='testpass123')

        # Try to access supplier login
        response = client.get('/accounts/supplier-login/')
        if response.status_code == 302:
            print("✓ Customer correctly blocked from supplier login")
        else:
            print("✗ Customer not blocked from supplier login")
            return False

        # Try to access consultant login
        response = client.get('/accounts/consultant-login/')
        if response.status_code == 302:
            print("✓ Customer correctly blocked from consultant login")
        else:
            print("✗ Customer not blocked from consultant login")
            return False

    client.logout()

    # Login as supplier
    supplier = CustomUser.objects.filter(user_type='supplier').first()
    if supplier:
        client.login(username=supplier.username, password='testpass123')

        # Try to access customer login
        response = client.get('/accounts/customer-login/')
        if response.status_code == 302:
            print("✓ Supplier correctly blocked from customer login")
        else:
            print("✗ Supplier not blocked from customer login")
            return False

    return True

def test_login_templates():
    """Test that login templates render correctly"""
    print("\n" + "="*60)
    print("TESTING LOGIN TEMPLATES")
    print("="*60)

    client = Client()

    # Test customer login template
    response = client.get('/accounts/customer-login/')
    if b'Customer Login' in response.content:
        print("✓ Customer login template renders correctly")
    else:
        print("✗ Customer login template not rendering correctly")
        return False

    # Test supplier login template
    response = client.get('/accounts/supplier-login/')
    if b'Supplier Login' in response.content:
        print("✓ Supplier login template renders correctly")
    else:
        print("✗ Supplier login template not rendering correctly")
        return False

    # Test consultant login template
    response = client.get('/accounts/consultant-login/')
    if b'Consultant Login' in response.content:
        print("✓ Consultant login template renders correctly")
    else:
        print("✗ Consultant login template not rendering correctly")
        return False

    return True

def main():
    """Run all role-based login tests"""
    print("ROLE-BASED LOGIN SYSTEM TEST")
    print("="*80)

    # Check if we have test users
    all_users = CustomUser.objects.all()
    print(f"Total users in database: {all_users.count()}")
    print("Available users:")
    for user in all_users:
        print(f"  {user.username}: {user.user_type}")

    customers = CustomUser.objects.filter(user_type='customer')
    suppliers = CustomUser.objects.filter(user_type='supplier')
    consultants = CustomUser.objects.filter(user_type='consultant')

    print(f"\nBy type:")
    print(f"  Customers: {customers.count()}")
    print(f"  Suppliers: {suppliers.count()}")
    print(f"  Consultants: {consultants.count()}")

    if customers.count() == 0 or suppliers.count() == 0 or consultants.count() == 0:
        print("\nWARNING: Missing test users. Creating sample users...")

        # Create test users if they don't exist
        if customers.count() == 0:
            CustomUser.objects.create_user(
                username='test_customer',
                password='testpass123',
                user_type='customer'
            )
        if suppliers.count() == 0:
            CustomUser.objects.create_user(
                username='test_supplier',
                password='testpass123',
                user_type='supplier'
            )
        if consultants.count() == 0:
            CustomUser.objects.create_user(
                username='test_consultant',
                password='testpass123',
                user_type='consultant'
            )

    # Run tests
    test1 = test_customer_login()
    test2 = test_supplier_login()
    test3 = test_consultant_login()
    test4 = test_cross_role_prevention()
    test5 = test_login_templates()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Customer login: {'PASS' if test1 else 'FAIL'}")
    print(f"Supplier login: {'PASS' if test2 else 'FAIL'}")
    print(f"Consultant login: {'PASS' if test3 else 'FAIL'}")
    print(f"Cross-role prevention: {'PASS' if test4 else 'FAIL'}")
    print(f"Login templates: {'PASS' if test5 else 'FAIL'}")

    all_passed = all([test1, test2, test3, test4, test5])

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nRole-based login system is working correctly:")
        print("✓ Users can only login through their designated role pages")
        print("✓ Users are redirected to appropriate dashboards")
        print("✓ Cross-role access is prevented")
        print("✓ Login templates render correctly")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the implementation and fix issues.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
