#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier
from apps.consultations.models import ConsultantApplication

User = get_user_model()

print("\n" + "="*80)
print("TESTING SHARON CONSULTANT SETUP")
print("="*80)

# Test 1: Check if Sharon user exists
sharon_user = User.objects.filter(username='sharon').first()
if sharon_user:
    print("✓ Sharon user exists")
    print(f"  - Username: {sharon_user.username}")
    print(f"  - User type: {sharon_user.user_type}")
    print(f"  - Is active: {sharon_user.is_active}")
else:
    print("✗ Sharon user does not exist")
    exit(1)

# Test 2: Check ConsultantApplication
consultant_app = ConsultantApplication.objects.filter(user=sharon_user).first()
if consultant_app:
    print("✓ ConsultantApplication exists")
    print(f"  - Full name: {consultant_app.full_name}")
    print(f"  - Processed: {consultant_app.processed}")
    print(f"  - Approved at: {consultant_app.approved_at}")
    print(f"  - Consultation rate: {consultant_app.consultation_rate}")
else:
    print("✗ ConsultantApplication does not exist")
    exit(1)

# Test 3: Check Supplier profile
supplier = Supplier.objects.filter(user=sharon_user).first()
if supplier:
    print("✓ Supplier profile exists")
    print(f"  - Consultation fee: {supplier.consultation_fee}")
    print(f"  - Location: {supplier.location}")
    print(f"  - Contact number: {supplier.contact_number}")
else:
    print("✗ Supplier profile does not exist")
    exit(1)

# Test 4: Check if Sharon appears in available consultants for booking
available_consultants = ConsultantApplication.objects.filter(processed=True, approved_at__isnull=False)
sharon_available = available_consultants.filter(user=sharon_user).exists()
if sharon_available:
    print("✓ Sharon is available for customer booking")
else:
    print("✗ Sharon is not available for customer booking")

print("\n" + "="*80)
print("TESTING COMPLETED")
print("="*80 + "\n")
