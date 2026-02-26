#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.suppliers.models import Supplier

print("\n" + "="*80)
print("UPDATING SPECIFIC USERS TO SUPPLIERS")
print("="*80)

# List of usernames to update
usernames = ['munene2', 'sharon', 'sharon2', 'klian12', 'munene33']
updated_count = 0

for username in usernames:
    try:
        # Special email for munene33
        email = 'victorjuniormunene@gmail.com' if username == 'munene33' else f'{username}@example.com'

        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': username.capitalize(),
                'user_type': 'supplier'
            }
        )

        if created:
            print(f"  ✓ Created new user: {username}")
        else:
            print(f"  ✓ Found existing user: {username}")

        # Update user type and password
        user.user_type = 'supplier'
        user.set_password('1234')
        user.save()

        # Ensure supplier profile exists
        supplier, supplier_created = Supplier.objects.get_or_create(
            user=user,
            defaults={
                'company_name': f'{username.capitalize()} Supplies',
                'location': 'Nairobi, Kenya'
            }
        )

        if supplier_created:
            print(f"    ✓ Created supplier profile for {username}")
        else:
            print(f"    ✓ Supplier profile already exists for {username}")

        updated_count += 1

    except Exception as e:
        print(f"  ✗ Error updating {username}: {str(e)}")

print(f"\n✅ Successfully updated {updated_count} users")
print("All specified users are now suppliers with password '1234'")
print("\n" + "="*80)
print("USER UPDATE COMPLETED!")
print("="*80 + "\n")
