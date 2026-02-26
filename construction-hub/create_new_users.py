#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser

print("\n" + "="*80)
print("CREATING NEW USERS")
print("="*80)

# Define users by role
customers = ['munene1', 'applicant1', 'ken', 'andklain']
suppliers = ['sharon', 'sharon2', 'klain12', 'munene2', 'junior']
consultants = ['victor22', 'applicant2', 'ane', 'ken']

password = '1234'
created_count = 0

# Create customers
print("\nCreating Customer Users:")
for username in customers:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': username.capitalize(),
            'user_type': 'customer'
        }
    )

    if created:
        print(f"  ✓ Created customer: {username}")
    else:
        print(f"  ✓ Found existing customer: {username}")

    user.user_type = 'customer'
    user.set_password(password)
    user.save()
    created_count += 1

# Create suppliers
print("\nCreating Supplier Users:")
for username in suppliers:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': username.capitalize(),
            'user_type': 'supplier'
        }
    )

    if created:
        print(f"  ✓ Created supplier: {username}")
    else:
        print(f"  ✓ Found existing supplier: {username}")

    user.user_type = 'supplier'
    user.set_password(password)
    user.save()
    created_count += 1

# Create consultants
print("\nCreating Consultant Users:")
for username in consultants:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': username.capitalize(),
            'user_type': 'consultant'
        }
    )

    if created:
        print(f"  ✓ Created consultant: {username}")
    else:
        print(f"  ✓ Found existing consultant: {username}")

    user.user_type = 'consultant'
    user.set_password(password)
    user.save()
    created_count += 1

print(f"\n✅ Successfully created/updated {created_count} users")
print("All users have password '1234'")
print("\n" + "="*80)
print("USER CREATION COMPLETED!")
print("="*80 + "\n")
