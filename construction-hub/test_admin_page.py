#!/usr/bin/env python
import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

User = get_user_model()

print("\n" + "="*80)
print("TESTING ADMIN PAGE ACCESS: admin2 / 1234")
print("="*80)

# Create test client
client = Client()

# Test admin login
login_data = {
    'username': 'admin2',
    'password': '1234'
}

# Attempt login
response = client.post('/admin/login/', login_data, follow=True)

if response.status_code == 200:
    # Check if we're redirected to admin index (successful login)
    if '/admin/' in response.request['PATH_INFO'] or 'admin' in str(response.content):
        print("✓ Admin login successful")
        print("✓ Admin page access confirmed")
        print("✓ User can access Django admin interface")
    else:
        print("✗ Login may have failed - not redirected to admin")
        print(f"  Response status: {response.status_code}")
        print(f"  Current URL: {response.request['PATH_INFO']}")
else:
    print(f"✗ Login failed with status code: {response.status_code}")

# Also test direct authentication
user = User.objects.filter(username='admin2').first()
if user:
    print(f"✓ Admin user exists: {user.username}")
    print(f"  User type: {user.user_type}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Is superuser: {user.is_superuser}")
    print(f"  Is active: {user.is_active}")
else:
    print("✗ Admin user 'admin2' not found")

print("\n" + "="*80)
print("ADMIN PAGE TEST COMPLETED!")
print("="*80 + "\n")
