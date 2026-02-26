#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.consultations.models import Consultant

print("\n" + "="*80)
print("UPDATING SPECIFIC USERS TO CONSULTANTS")
print("="*80)

# List of usernames to update
usernames = ['victor22', 'applicant2', 'ken ken']
updated_count = 0

for username in usernames:
    try:
        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username.replace(" ", "").lower()}@example.com',
                'first_name': username.split()[0].capitalize() if ' ' in username else username.capitalize(),
                'last_name': username.split()[1].capitalize() if ' ' in username else '',
                'user_type': 'consultant'
            }
        )

        if created:
            print(f"  ✓ Created new user: {username}")
        else:
            print(f"  ✓ Found existing user: {username}")

        # Update user type and password
        user.user_type = 'consultant'
        user.set_password('1234')
        user.save()

        # Ensure consultant profile exists
        consultant, consultant_created = Consultant.objects.get_or_create(
            user=user,
            defaults={
                'specialization': 'General Construction Consulting',
                'experience_years': 5,
                'certifications': 'Construction Management Certification',
                'bio': f'Professional construction consultant with expertise in various construction projects.'
            }
        )

        if consultant_created:
            print(f"    ✓ Created consultant profile for {username}")
        else:
            print(f"    ✓ Consultant profile already exists for {username}")

        updated_count += 1

    except Exception as e:
        print(f"  ✗ Error updating {username}: {str(e)}")

print(f"\n✅ Successfully updated {updated_count} users")
print("All specified users are now consultants with password '1234'")
print("\n" + "="*80)
print("USER UPDATE COMPLETED!")
print("="*80 + "\n")
