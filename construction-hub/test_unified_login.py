#!/usr/bin/env python
"""
Test script to verify that the unified login redirects users based on their role.
"""
import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_unified_login():
    """Test that unified login redirects based on user role."""
    client = Client()

    # Test with customer user
    try:
        customer = User.objects.filter(user_type='customer').first()
        if customer:
            client.login(username=customer.username, password='1234')
            response = client.post('/accounts/login/', {
                'username': customer.username,
                'password': '1234'
            }, follow=True)
            print(f"Customer login redirect: {response.redirect_chain}")
            if 'customer' in str(response.redirect_chain).lower():
                print("✓ Customer correctly redirected")
            else:
                print("✗ Customer not redirected correctly")
        else:
            print("⚠️ No customer user found for testing")
    except Exception as e:
        print(f"Error testing customer login: {e}")

    # Test with supplier user
    try:
        supplier = User.objects.filter(user_type='supplier').first()
        if supplier:
            client.login(username=supplier.username, password='1234')
            response = client.post('/accounts/login/', {
                'username': supplier.username,
                'password': '1234'
            }, follow=True)
            print(f"Supplier login redirect: {response.redirect_chain}")
            if 'supplier' in str(response.redirect_chain).lower():
                print("✓ Supplier correctly redirected")
            else:
                print("✗ Supplier not redirected correctly")
        else:
            print("⚠️ No supplier user found for testing")
    except Exception as e:
        print(f"Error testing supplier login: {e}")

    # Test with consultant user
    try:
        consultant = User.objects.filter(user_type='consultant').first()
        if consultant:
            client.login(username=consultant.username, password='1234')
            response = client.post('/accounts/login/', {
                'username': consultant.username,
                'password': '1234'
            }, follow=True)
            print(f"Consultant login redirect: {response.redirect_chain}")
            if 'consultant' in str(response.redirect_chain).lower():
                print("✓ Consultant correctly redirected")
            else:
                print("✗ Consultant not redirected correctly")
        else:
            print("⚠️ No consultant user found for testing")
    except Exception as e:
        print(f"Error testing consultant login: {e}")

    print("\nUnified login test completed.")

if __name__ == '__main__':
    test_unified_login()
