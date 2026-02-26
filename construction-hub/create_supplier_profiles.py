#!/usr/bin/env python
"""
Script to create missing Supplier profiles for users with user_type='supplier'
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.suppliers.models import Supplier

def create_missing_supplier_profiles():
    """Create Supplier profiles for supplier users who don't have them"""
    print("Checking for supplier users without profiles...")

    # Find supplier users without profiles
    supplier_users = CustomUser.objects.filter(user_type='supplier')
    print(f'Found {supplier_users.count()} supplier users')

    created_count = 0
    existing_count = 0

    for user in supplier_users:
        if not Supplier.objects.filter(user=user).exists():
            try:
                supplier = Supplier.objects.create(
                    user=user,
                    company_name=user.username,
                    location='',
                    contact_number=''
                )
                print(f'✓ Created supplier profile for {user.username}')
                created_count += 1
            except Exception as e:
                print(f'✗ Error creating profile for {user.username}: {e}')
        else:
            print(f'○ Supplier profile already exists for {user.username}')
            existing_count += 1

    print(f"\nSummary:")
    print(f"- Created: {created_count} profiles")
    print(f"- Existing: {existing_count} profiles")
    print("- Total supplier users checked:", supplier_users.count())

if __name__ == '__main__':
    create_missing_supplier_profiles()
