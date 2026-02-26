#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier

User = get_user_model()

print("Checking supplier users...")

# Check all users with supplier role
supplier_users = User.objects.filter(user_type='supplier')
print(f"Found {supplier_users.count()} users with supplier role")

for user in supplier_users:
    print(f"\nUser: {user.username}")
    print(f"User type: {user.user_type}")
    print(f"is_supplier: {user.is_supplier}")

    try:
        supplier = Supplier.objects.get(user=user)
        print(f"Supplier object exists: {supplier.company_name}")
        print(f"Supplier location: {supplier.location}")
        print(f"Supplier contact: {supplier.contact_number}")
    except Supplier.DoesNotExist:
        print("ERROR: Supplier object does not exist for this user!")

# Check specific supplier1 user
try:
    supplier1 = User.objects.get(username='supplier1')
    print(f"\n=== SUPPLIER1 DETAILS ===")
    print(f"Username: {supplier1.username}")
    print(f"User type: {supplier1.user_type}")
    print(f"is_supplier: {supplier1.is_supplier}")
    print(f"is_active: {supplier1.is_active}")

    try:
        supplier_obj = Supplier.objects.get(user=supplier1)
        print(f"Supplier object: {supplier_obj.company_name}")
    except Supplier.DoesNotExist:
        print("ERROR: No Supplier object for supplier1!")

except User.DoesNotExist:
    print("ERROR: supplier1 user does not exist!")
