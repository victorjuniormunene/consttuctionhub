#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.suppliers.models import Supplier

print("\n" + "="*100)
print("ALL SUPPLIERS IN THE SYSTEM WITH USERNAME AND PASSWORD INFO")
print("="*100)

# Get all suppliers
suppliers = Supplier.objects.select_related('user').all().order_by('user__username')

if suppliers.exists():
    print(f"\nFound {suppliers.count()} suppliers:\n")
    print("-" * 100)
    print(f"{'Username':<15} {'Full Name':<20} {'Company Name':<25} {'Password':<15}")
    print("-" * 100)

    for supplier in suppliers:
        user = supplier.user
        full_name = user.get_full_name() or 'N/A'

        # Check if this is one of the updated users
        if user.username in ['munene2', 'sharon', 'sharon2', 'klian12']:
            password_info = '1234'
        else:
            password_info = 'Not specified'

        print(f"{user.username:<15} {full_name:<20} {supplier.company_name:<25} {password_info:<15}")

    print("-" * 100)
    print("\nNote: Passwords for munene2, sharon, sharon2, and klian12 have been set to '1234'")
    print("Other suppliers may have different passwords set during registration.")

else:
    print("\nNo suppliers found in the system.")

print("\n" + "="*100)
print("SUPPLIER LIST COMPLETED!")
print("="*100 + "\n")
