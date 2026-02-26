#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')

# Setup Django
django.setup()

from django.test import Client
from django.urls import reverse
from apps.accounts.models import CustomUser

def test_password_reset():
    client = Client()

    # Test if the password reset URL can be reversed
    try:
        url = reverse('accounts:password_reset')
        print(f"Password reset URL: {url}")
    except Exception as e:
        print(f"Error reversing password reset URL: {e}")
        return False

    # Test if the password reset confirm URL can be reversed
    try:
        url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': 'test', 'token': 'test'})
        print(f"Password reset confirm URL: {url}")
    except Exception as e:
        print(f"Error reversing password reset confirm URL: {e}")
        return False

    # Create a test user if it doesn't exist
    if not CustomUser.objects.filter(email='test@example.com').exists():
        CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpass123')

    # Test the password reset form submission
    response = client.post('/accounts/password_reset/', {'email': 'test@example.com'})
    print(f"Password reset POST response status: {response.status_code}")

    if response.status_code == 302:  # Redirect to done page
        print("Password reset form submitted successfully")
        return True
    else:
        print("Password reset form submission failed")
        print(f"Response content: {response.content.decode()}")
        return False

if __name__ == '__main__':
    success = test_password_reset()
    if success:
        print("Password reset test passed!")
    else:
        print("Password reset test failed!")
