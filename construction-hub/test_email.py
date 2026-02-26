#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

def test_email():
    print("Testing Gmail SMTP configuration...")

    # Create a test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'victorjuniormunene@gmail.com',
            'user_type': 'customer'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('✓ Test user created')
    else:
        print('✓ Test user already exists')

    # Test email sending
    try:
        send_mail(
            'Test Password Reset - Construction Hub',
            'This is a test email to verify Gmail SMTP configuration for password reset functionality.\n\nIf you received this email, the configuration is working correctly!',
            settings.DEFAULT_FROM_EMAIL,
            ['victorjuniormunene@gmail.com'],
            fail_silently=False,
        )
        print('✓ Test email sent successfully!')
        print('✓ Gmail SMTP configuration is working')
        return True
    except Exception as e:
        print(f'✗ Email sending failed: {e}')
        return False

if __name__ == '__main__':
    success = test_email()
    sys.exit(0 if success else 1)
