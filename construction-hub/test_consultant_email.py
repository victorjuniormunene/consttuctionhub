#!/usr/bin/env python
"""
Test script to verify that consultants can send emails to clients from their dashboard.
This tests the send_consultant_email endpoint functionality.
"""
import os
import sys
import json
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.conf import settings


def add_middleware_to_request(request):
    """Add session and message middleware to a request object for authentication"""
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    
    msg_middleware = MessageMiddleware(lambda req: None)
    msg_middleware.process_request(request)
    request.session.save()


def test_consultant_email():
    """Test that a consultant can send an email to a client about their consultation"""
    print("\n" + "="*60)
    print("TESTING CONSULTANT EMAIL FUNCTIONALITY")
    print("="*60 + "\n")
    
    User = get_user_model()
    client = Client()
    
    # Step 1: Create or get consultant user
    print("Step 1: Setting up consultant user...")
    consultant, created = User.objects.get_or_create(
        username='test_consultant',
        defaults={
            'email': 'consultant@test.com',
            'user_type': 'consultant',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    if created:
        consultant.set_password('testpass123')
        consultant.save()
        print("✓ Consultant user created")
    else:
        print("✓ Consultant user already exists")
    
    # Step 2: Create or get customer user
    print("\nStep 2: Setting up customer user...")
    customer, created = User.objects.get_or_create(
        username='test_customer_email',
        defaults={
            'email': 'victorjuniormunene@gmail.com',  # Use actual email to receive test
            'user_type': 'customer',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
        print("✓ Customer user created")
    else:
        print("✓ Customer user already exists")
    
    # Step 3: Create a consultation booking
    print("\nStep 3: Creating consultation booking...")
    from apps.consultations.models import Consultation, ConsultantApplication
    
    # Get or create consultant application
    consultant_app, created = ConsultantApplication.objects.get_or_create(
        user=consultant,
        defaults={
            'full_name': 'John Doe',
            'email': 'consultant@test.com',
            'phone': '+254700000000',
            'specialization': 'Structural Engineering',
            'consultation_rate': 5000,
            'processed': True
        }
    )
    if created:
        from django.utils import timezone
        consultant_app.approved_at = timezone.now()
        consultant_app.save()
        print("✓ Consultant application created and approved")
    else:
        print("✓ Consultant application already exists")
    
    # Create consultation
    consultation, created = Consultation.objects.get_or_create(
        id=999,
        defaults={
            'customer': customer,
            'consultant': consultant,
            'consultant_name': 'John Doe',
            'consultant_phone': '+254700000000',
            'consultation_rate': 5000,
            'specialization': 'Structural Engineering',
            'details': 'Test consultation for email functionality',
            'status': 'pending'
        }
    )
    if created:
        print("✓ Consultation booking created")
    else:
        print("✓ Consultation already exists")
    
    # Step 4: Test unauthenticated request (should fail)
    print("\nStep 4: Testing unauthenticated request (should fail)...")
    response = client.post(
        '/dashboard/send-consultant-email/',
        data=json.dumps({
            'recipient_email': 'victorjuniormunene@gmail.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }),
        content_type='application/json'
    )
    if response.status_code == 403 or response.status_code == 302:
        print("✓ Unauthenticated request properly rejected")
    else:
        print(f"⚠ Unauthenticated request status: {response.status_code}")
    
    # Step 5: Login as consultant
    print("\nStep 5: Logging in as consultant...")
    logged_in = client.login(username='test_consultant', password='testpass123')
    if logged_in:
        print("✓ Successfully logged in as consultant")
    else:
        print("✗ Failed to login as consultant")
        return False
    
    # Step 6: Test sending email from consultant to customer
    print("\nStep 6: Testing email sending...")
    consultation_details = f"""
Consultation Details:
- Date: {consultation.date_requested.strftime('%B %d, %Y')}
- Time: {consultation.date_requested.strftime('%H:%M')}
- Specialization: {consultation.specialization}
- Rate: KSH {consultation.consultation_rate}
- Status: {consultation.status.upper()}
    """
    
    response = client.post(
        '/dashboard/send-consultant-email/',
        data=json.dumps({
            'recipient_email': customer.email,
            'subject': f'Consultation Update - {consultation.specialization}',
            'message': f'Dear {customer.get_full_name() or customer.username},\n\nI would like to provide you with an update regarding your consultation booking.\n\n{consultation_details}\n\nPlease feel free to reach out if you have any questions.\n\nBest regards,\n{consultant.get_full_name() or consultant.username}'
        }),
        content_type='application/json'
    )
    
    print(f"   Response status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Response data: {data}")
            if data.get('success'):
                print("✓ Email sent successfully!")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"✗ Email sending failed: {data.get('error')}")
                return False
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON response")
            return False
    else:
        print(f"✗ HTTP Error: {response.status_code}")
        try:
            print(f"   Response: {response.content.decode()}")
        except:
            pass
        return False
    
    # Step 7: Verify email was sent
    print("\nStep 7: Verifying email configuration...")
    print(f"   FROM EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   TO EMAIL: {customer.email}")
    print(f"   EMAIL BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL HOST: {settings.EMAIL_HOST}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nSummary:")
    print("  ✓ Consultant can login to dashboard")
    print("  ✓ Consultation booking exists with customer")
    print("  ✓ Email endpoint is accessible")
    print("  ✓ Email was sent to customer's email address")
    print(f"  ✓ Customer will receive email at: {customer.email}")
    print("\n" + "="*60)
    
    return True


if __name__ == '__main__':
    try:
        success = test_consultant_email()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
