#!/usr/bin/env python
"""
Create a superuser with the following details:
- Username: admin2
- Password: 1234
- Email: victorjuniormunene@gmail.com
- Phone: 0112725677
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
username = 'admin2'
email = 'victorjuniormunene@gmail.com'
password = '1234'
phone_number = '0112725677'

try:
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.email = email
        user.phone_number = phone_number
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✓ Updated superuser: {username}")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number
        )
        print(f"✓ Created superuser: {username}")
    
    print(f"\nSuperuser Details:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Phone: {phone_number}")
    print(f"  Password: {password}")
    print(f"\nYou can now login at /admin/ or /accounts/login/")
    
except Exception as e:
    print(f"✗ Error creating superuser: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
