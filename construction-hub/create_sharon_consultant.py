#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier

User = get_user_model()

print("\n" + "="*80)
print("CREATING CONSULTANT: SHARON")
print("="*80)

# Check if user already exists
if User.objects.filter(username='sharon').exists():
    print("User 'sharon' already exists.")
else:
    # Create user
    user = User.objects.create_user(
        username='sharon',
        password='1234',
        user_type='consultant'
    )
    print(f"Created user: {user.username} with user_type: {user.user_type}")

    # Create consultant application
    from apps.consultations.models import ConsultantApplication
    from django.utils import timezone

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

print("\n" + "="*80)
print("CONSULTANT CREATION COMPLETED!")
print("="*80 + "\n")
