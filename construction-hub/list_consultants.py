#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier

print("\n" + "="*80)
print("ALL CONSULTANTS IN DATABASE")
print("="*80)

consultants = Supplier.objects.filter(consultation_fee__gt=0).select_related('user')

if not consultants:
    print("No consultants found.")
else:
    for consultant in consultants:
        print(f"Username: {consultant.user.username}")
        print(f"Email: {consultant.user.email}")
        print(f"Full Name: {consultant.user.get_full_name() or consultant.user.username}")
        print(f"Consultation Fee: {consultant.consultation_fee}")
        print(f"Location: {consultant.location}")
        print(f"Contact: {consultant.contact_number}")
        print("-" * 40)

print(f"\nTotal consultants: {consultants.count()}")
print("="*80 + "\n")
