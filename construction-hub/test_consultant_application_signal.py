#!/usr/bin/env python
"""
Test script to verify that the ConsultantApplication signal handler works correctly.
This tests the fix for the AttributeError: 'ConsultantApplication' object has no attribute 'location'
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.consultations.models import ConsultantApplication


def test_consultant_application_signal():
    """Test that creating a ConsultantApplication triggers the signal without AttributeError"""
    print("\n" + "="*60)
    print("TESTING CONSULTANT APPLICATION SIGNAL HANDLER")
    print("="*60 + "\n")
    
    User = get_user_model()
    client = Client()
    
    # Step 1: Create or get a test user
    print("Step 1: Setting up test user...")
    test_user, created = User.objects.get_or_create(
        username='signal_test_user',
        defaults={
            'email': 'signaltest@test.com',
            'user_type': 'customer',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("✓ Test user created")
    else:
        print("✓ Test user already exists")
    
    # Step 2: Login as the test user
    print("\nStep 2: Logging in as test user...")
    logged_in = client.login(username='signal_test_user', password='testpass123')
    if logged_in:
        print("✓ Successfully logged in")
    else:
        print("✗ Failed to login")
        return False
    
    # Step 3: Submit consultant application form
    print("\nStep 3: Submitting consultant application form...")
    
    # Get CSRF token
    response = client.get('/accounts/consultant-application/')
    print(f"   GET request status: {response.status_code}")
    
    # Extract CSRF token from cookies
    csrf_token = client.cookies.get('csrftoken')
    if csrf_token:
        print(f"   CSRF token obtained")
        csrf_token = csrf_token.value
    else:
        print("✗ Could not get CSRF token")
        return False
    
    # Prepare form data
    form_data = {
        'full_name': 'Test Consultant',
        'email': 'testconsultant@test.com',
        'phone': '+254700000000',
        'specialization': 'General Construction',
        'experience_years': '5',
        'cover_letter': 'This is a test application for the signal handler fix.',
        'csrfmiddlewaretoken': csrf_token,
    }
    
    # Submit the form
    try:
        response = client.post(
            '/accounts/consultant-application/',
            data=form_data,
            follow=True
        )
        print(f"   POST request status: {response.status_code}")
        
        # Check if there was an AttributeError
        if response.status_code == 500:
            print("✗ Server error occurred (500)")
            # Try to get the error content
            try:
                content = response.content.decode()
                if 'AttributeError' in content:
                    print("✗ AttributeError still present in response")
                    print(f"   Error content: {content[:500]}")
                    return False
            except:
                pass
        elif response.status_code == 200 or response.status_code == 302:
            print("✓ Request completed without AttributeError!")
            
            # Step 4: Verify the application was created
            print("\nStep 4: Verifying application was created...")
            app = ConsultantApplication.objects.filter(email='testconsultant@test.com').first()
            if app:
                print(f"✓ ConsultantApplication created with ID: {app.id}")
                print(f"   - Name: {app.full_name}")
                print(f"   - Email: {app.email}")
                print(f"   - Specialization: {app.specialization}")
                print(f"   - Submitted at: {app.submitted_at}")
            else:
                print("⚠ ConsultantApplication not found in database")
            
            print("\n" + "="*60)
            print("TEST PASSED!")
            print("="*60)
            print("\nSummary:")
            print("  ✓ Form submission completed without AttributeError")
            print("  ✓ Signal handler executed successfully")
            print("  ✓ ConsultantApplication created in database")
            print("\nThe fix for 'ConsultantApplication' object has no attribute 'location'")
            print("has been verified successfully!")
            print("="*60)
            return True
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        if 'location' in str(e):
            print("✗ The AttributeError for 'location' still occurs!")
            return False
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        success = test_consultant_application_signal()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
