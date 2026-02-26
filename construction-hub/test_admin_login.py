#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

print("\n" + "="*80)
print("TESTING ADMIN LOGIN: admin2 / 1234")
print("="*80)

# First check if user exists
try:
    user_obj = User.objects.get(username='admin2')
    print(f"✓ User 'admin2' exists in database")
    print(f"  User type: {user_obj.user_type}")
    print(f"  Is staff: {user_obj.is_staff}")
    print(f"  Is superuser: {user_obj.is_superuser}")
    print(f"  Is active: {user_obj.is_active}")
    print(f"  Password check: {user_obj.check_password('1234')}")

    # Test authentication
    user = authenticate(username='admin2', password='1234')
    if user is not None:
        print("✓ Authentication successful")
        print("✓ Admin page access should work with these credentials")
    else:
        print("✗ Authentication failed despite user existing")
        print("  This might indicate an authentication backend issue")

except User.DoesNotExist:
    print("✗ User 'admin2' does not exist in database")
    print("  Run 'python create_admin2.py' to create the admin user")

print("\n" + "="*80)
print("ADMIN LOGIN TEST COMPLETED!")
print("="*80 + "\n")
