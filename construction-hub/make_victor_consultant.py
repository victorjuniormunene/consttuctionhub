#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.consultations.models import ConsultantApplication
from apps.suppliers.models import Supplier

def make_victor_consultant():
    User = get_user_model()

    # Check if Victor exists
    try:
        victor = User.objects.get(username='victor')
        print(f"Victor already exists: {victor.username}")
    except User.DoesNotExist:
        # Create Victor user
        victor = User.objects.create_user(
            username='victor',
            email='victor@constructionhub.com',
            password='victorpass123',
            first_name='Victor',
            last_name='Munene',
            role='consultant',
            is_consultant=True
        )
        print(f"Created Victor user: {victor.username}")

    # Ensure Victor has consultant role
    victor.user_type = 'consultant'
    victor.save()

    # Check if Victor has a consultant application
    consultant_app, created = ConsultantApplication.objects.get_or_create(
        user=victor,
        defaults={
            'full_name': 'Victor Munene',
            'email': 'victor@constructionhub.com',
            'specialization': 'Architectural Plans',
            'experience_years': 5,
            'consultation_rate': 5000.00,
            'processed': True,
            'approved_at': django.utils.timezone.now()
        }
    )

    if created:
        print("Created consultant application for Victor")
    else:
        # Update existing application
        consultant_app.specialization = 'Architectural Plans'
        consultant_app.consultation_rate = 5000.00
        consultant_app.approved = True
        consultant_app.approved_at = django.utils.timezone.now()
        consultant_app.save()
        print("Updated existing consultant application for Victor")

    # Ensure Supplier with consultation_fee > 0 exists (for compatibility with other parts of the system)
    supplier = Supplier.objects.filter(user=victor).first()
    if not supplier:
        supplier = Supplier.objects.create(
            user=victor,
            consultation_fee=5000.00,  # Set a consultation fee > 0 to make them a consultant
            location='Nairobi',
            contact_number='0712345678'
        )
        print(f"Created supplier/consultant: {supplier.user.username} with consultation fee: {supplier.consultation_fee}")
    elif supplier.consultation_fee == 0:
        supplier.consultation_fee = 5000.00
        supplier.save()
        print(f"Updated supplier consultation fee: {supplier.consultation_fee}")
    else:
        print(f"Supplier already exists with consultation fee: {supplier.consultation_fee}")

    print(f"Victor is now a consultant for Architectural Plans with rate KSH {consultant_app.consultation_rate}")
    print("He is available for booking consultations.")

if __name__ == '__main__':
    make_victor_consultant()
