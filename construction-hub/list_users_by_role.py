#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser

def list_users_by_role():
    """List all users grouped by their roles"""

    print("="*80)
    print("USERS BY ROLE")
    print("="*80)

    # Get all users
    all_users = CustomUser.objects.all().order_by('user_type', 'username')

    # Group by role
    roles = ['customer', 'supplier', 'consultant', 'admin']

    for role in roles:
        role_users = all_users.filter(user_type=role)
        if role_users.exists():
            print(f"\n{role.upper()}S ({role_users.count()}):")
            print("-" * 40)
            for user in role_users:
                print(f"  Username: {user.username}")
                print(f"  Full Name: {user.get_full_name() or 'N/A'}")
                print(f"  Email: {user.email or 'N/A'}")
                print(f"  Phone: {user.phone_number or 'N/A'}")
                print(f"  Company: {user.company_name or 'N/A'}")
                print(f"  Location: {user.location or 'N/A'}")
                print()

    print("="*80)
    print(f"TOTAL USERS: {all_users.count()}")
    print("="*80)

if __name__ == '__main__':
    list_users_by_role()
