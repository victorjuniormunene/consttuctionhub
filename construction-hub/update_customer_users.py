#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser

print("\n" + "="*80)
print("UPDATING SPECIFIC USERS TO CUSTOMERS")
print("="*80)

# List of usernames to update
usernames = ['munene1', 'applicant1']
updated_count = 0

for username in usernames:
    try:
        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': username.capitalize(),
                'user_type': 'customer'
            }
        )

        if created:
            print(f"  ✓ Created new user: {username}")
        else:
            print(f"  ✓ Found existing user: {username}")

        # Update user type and password
        user.user_type = 'customer'
        user.set_password('1234')
        user.save()

        updated_count += 1

    except Exception as e:
        print(f"  ✗ Error updating {username}: {str(e)}")

print(f"\n✅ Successfully updated {updated_count} users")
print("All specified users are now customers with password '1234'")
print("\n" + "="*80)
print("USER UPDATE COMPLETED!")
print("="*80 + "\n")
