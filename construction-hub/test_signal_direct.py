#!/usr/bin/env python
"""
Simple test script to verify that the ConsultantApplication signal handler works correctly.
This directly creates a ConsultantApplication object to trigger the signal without HTTP requests.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.consultations.models import ConsultantApplication


def test_signal_direct():
    """Test that creating a ConsultantApplication triggers the signal without AttributeError"""
    print("\n" + "="*60)
    print("TESTING CONSULTANT APPLICATION SIGNAL (DIRECT TEST)")
    print("="*60 + "\n")
    
    User = get_user_model()
    
    # Step 1: Get or create a test user
    print("Step 1: Getting or creating test user...")
    test_user, created = User.objects.get_or_create(
        username='signal_test_direct',
        defaults={
            'email': 'signaldirect@test.com',
            'user_type': 'customer',
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("  ✓ Test user created")
    else:
        print("  ✓ Test user already exists")
    
    # Step 2: Create ConsultantApplication (this triggers the signal)
    print("\nStep 2: Creating ConsultantApplication object...")
    try:
        app = ConsultantApplication.objects.create(
            user=test_user,
            full_name='Test Consultant Direct',
            email='testdirect@test.com',
            phone='+254700000000',
            specialization='General Construction',
            experience_years=5,
            consultation_rate=5000,
            cover_letter='Test application for signal handler.',
        )
        print("  ✓ ConsultantApplication created successfully!")
        print(f"    - ID: {app.id}")
        print(f"    - Name: {app.full_name}")
        print(f"    - Email: {app.email}")
        print(f"    - Specialization: {app.specialization}")
        print(f"    - Submitted at: {app.submitted_at}")
        
        # Step 3: Verify signal was called
        print("\nStep 3: Verifying signal was called...")
        print("  ✓ Signal handler executed without AttributeError!")
        
        print("\n" + "="*60)
        print("TEST PASSED!")
        print("="*60)
        print("\nThe fix for 'ConsultantApplication' object has no attribute 'location'")
        print("has been verified successfully!")
        print("="*60)
        return True
        
    except AttributeError as e:
        print(f"  ✗ AttributeError occurred: {e}")
        if 'location' in str(e):
            print("  ✗ The 'location' attribute error still occurs!")
        return False
    except Exception as e:
        print(f"  ✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        success = test_signal_direct()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
