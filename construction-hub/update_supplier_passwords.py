#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth.models import User
from apps.suppliers.models import Supplier

print("\n" + "="*80)
print("UPDATING SUPPLIER PASSWORDS")
print("="*80)

suppliers = Supplier.objects.filter(user__username='munene2')
updated_count = 0

for supplier in suppliers:
    user = supplier.user
    user.set_password('1234')
    user.save()
    print(f"  ✓ Updated password for {user.username} ({supplier.company_name})")
    updated_count += 1

print(f"\n✅ Updated passwords for {updated_count} suppliers")
print("All supplier passwords are now '1234'")
print("\n" + "="*80)
print("PASSWORD UPDATE COMPLETED!")
print("="*80 + "\n")
