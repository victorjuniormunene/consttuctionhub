#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier
from apps.consultations.models import ConsultantApplication
from django.utils import timezone

User = get_user_model()

print("\n" + "="*80)
print("SETTING UP SHARON AS CONSULTANT FOR CUSTOMER BOOKING")
print("="*80)

# Check if user already exists
user = User.objects.filter(username='sharon').first()
if not user:
    # Create user
    user = User.objects.create_user(
        username='sharon',
        password='1234',
        user_type='consultant'
    )
    print(f"Created user: {user.username} with user_type: {user.user_type}")
else:
    print(f"User 'sharon' already exists with user_type: {user.user_type}")

# Ensure ConsultantApplication exists and is approved
consultant_app = ConsultantApplication.objects.filter(user=user).first()
if not consultant_app:
    consultant_app = ConsultantApplication.objects.create(
        user=user,
        full_name='Sharon Consultant',
        email='sharon@example.com',
        phone='0712345678',
        specialization='Construction Consulting',
        experience_years=5,
        consultation_rate=1000.00,
        processed=True,
        approved_at=timezone.now()
    )
    print(f"Created consultant application: {consultant_app.full_name} with rate: {consultant_app.consultation_rate}")
elif not consultant_app.processed or consultant_app.approved_at is None:
    consultant_app.processed = True
    consultant_app.approved_at = timezone.now()
    consultant_app.save()
    print(f"Updated consultant application to approved: {consultant_app.full_name}")
else:
    print(f"Consultant application already exists and is approved: {consultant_app.full_name}")

# Ensure Supplier with consultation_fee > 0 exists (for compatibility with other parts of the system)
supplier = Supplier.objects.filter(user=user).first()
if not supplier:
    supplier = Supplier.objects.create(
        user=user,
        consultation_fee=1000.00,  # Set a consultation fee > 0 to make them a consultant
        location='Nairobi',
        contact_number='0712345678'
    )
    print(f"Created supplier/consultant: {supplier.user.username} with consultation fee: {supplier.consultation_fee}")
elif supplier.consultation_fee == 0:
    supplier.consultation_fee = 1000.00
    supplier.save()
    print(f"Updated supplier consultation fee: {supplier.consultation_fee}")
else:
    print(f"Supplier already exists with consultation fee: {supplier.consultation_fee}")

print("\n✅ Sharon is now available for booking as a consultant by customers!")
print("="*80 + "\n")
