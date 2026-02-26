#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier

User = get_user_model()

print("\n" + "="*80)
print("CREATING CONSULTANT: SHARON2")
print("="*80)

# Check if user already exists
if User.objects.filter(username='sharon2').exists():
    print("User 'sharon2' already exists.")
else:
    # Create user
    user = User.objects.create_user(
        username='sharon2',
        password='1234',
        user_type='consultant'
    )
    print(f"Created user: {user.username}")

    # Create supplier with consultation fee
    supplier = Supplier.objects.create(
        user=user,
        consultation_fee=1000,  # Set a consultation fee > 0 to make them a consultant
        location='Nairobi',
        contact_number='0712345678'
    )
    print(f"Created supplier/consultant: {supplier.user.username} with consultation fee: {supplier.consultation_fee}")

print("\n" + "="*80)
print("CONSULTANT CREATION COMPLETED!")
print("="*80 + "\n")
