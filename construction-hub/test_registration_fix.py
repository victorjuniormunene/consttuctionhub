#!/usr/bin/env python
"""
Test script to verify the NoReverseMatch error is fixed in the registration view.
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.forms import UserRegistrationForm

def test_registration_redirect():
    """Test that registration redirects correctly without NoReverseMatch error."""
    client = Client()

    # Test data for registration
    registration_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'user_type': 'customer',
        'first_name': 'Test',
        'last_name': 'User',
    }

    print("Testing registration POST request...")

    try:
        # Make POST request to registration endpoint
        response = client.post('/accounts/register/', data=registration_data, follow=True)

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Registration form rendered successfully")
        elif response.status_code in [301, 302]:
            print("✅ Registration redirect successful")
            print(f"Redirected to: {response.redirect_chain}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")

        # Check if there are any redirect errors in the response
        if hasattr(response, 'content') and b'NoReverseMatch' in response.content:
            print("❌ NoReverseMatch error still present in response")
            return False
        else:
            print("✅ No NoReverseMatch errors found")

        return True

    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

def test_url_resolution():
    """Test that the dashboard URL can be resolved correctly."""
    try:
        # Test that we can resolve the dashboard URL
        dashboard_url = reverse('accounts:dashboard')
        print(f"✅ Dashboard URL resolved successfully: {dashboard_url}")
        return True
    except Exception as e:
        print(f"❌ Error resolving dashboard URL: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing Django registration fix...")
    print("=" * 50)

    # Test URL resolution
    url_test = test_url_resolution()
    print()

    # Test registration
    registration_test = test_registration_redirect()
    print()

    if url_test and registration_test:
        print("🎉 All tests passed! The NoReverseMatch error has been fixed.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. The issue may not be fully resolved.")
        sys.exit(1)
