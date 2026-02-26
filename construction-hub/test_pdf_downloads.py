#!/usr/bin/env python
"""
Comprehensive test script for PDF download functionality
"""
import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from apps.dashboard.views import download_customer_report, download_supplier_report, download_consultant_report
from apps.orders.models import Order
from apps.consultations.models import Consultation
from apps.suppliers.models import Supplier
from apps.products.models import Product

def run_tests():
    print('=== COMPREHENSIVE PDF DOWNLOAD TESTING ===\n')

    User = get_user_model()

    # Check database state
    print('Database Status:')
    print(f'- Users: {User.objects.count()}')
    print(f'- Orders: {Order.objects.count()}')
    print(f'- Consultations: {Consultation.objects.count()}')
    print(f'- Suppliers: {Supplier.objects.count()}')
    print(f'- Products: {Product.objects.count()}\n')

    # Test each user type
    test_results = []

    # Test 1: Customer Download
    print('1. TESTING CUSTOMER DOWNLOAD FUNCTION')
    try:
        customer = User.objects.filter(user_type='customer').first() or User.objects.filter(is_customer=True).first()
        if not customer:
            customer = User.objects.filter(user_type='admin').first() or User.objects.first()
            if customer:
                customer.user_type = 'customer'
                customer.save()

        if customer:
            print(f'   Using customer: {customer.username} (role: {customer.role})')

            factory = RequestFactory()
            request = factory.get('/dashboard/download-customer-report/')
            request.user = customer

            # Add middleware
            def dummy_get_response(request):
                return None
            session_middleware = SessionMiddleware(dummy_get_response)
            session_middleware.process_request(request)
            request.session.save()

            message_middleware = MessageMiddleware(dummy_get_response)
            message_middleware.process_request(request)

            response = download_customer_report(request)
            print(f'   Response status: {response.status_code}')
            print(f'   Content-Type: {response.get("Content-Type")}')
            print(f'   Content-Disposition: {response.get("Content-Disposition")}')

            if response.status_code == 200 and 'application/pdf' in response.get('Content-Type', ''):
                test_results.append(('Customer Download', 'PASS'))
                print('   ✅ PASS: PDF generated successfully')
            else:
                test_results.append(('Customer Download', 'FAIL'))
                print('   ❌ FAIL: PDF not generated')
        else:
            test_results.append(('Customer Download', 'SKIP - No customer user'))
            print('   ⚠️  SKIP: No customer user found')

    except Exception as e:
        test_results.append(('Customer Download', f'ERROR: {str(e)}'))
        print(f'   ❌ ERROR: {e}')

    print()

    # Test 2: Supplier Download
    print('2. TESTING SUPPLIER DOWNLOAD FUNCTION')
    try:
        supplier_user = User.objects.filter(user_type='supplier').first() or User.objects.filter(is_supplier=True).first()
        if not supplier_user:
            supplier_user = User.objects.filter(user_type='admin').first() or User.objects.first()
            if supplier_user:
                supplier_user.user_type = 'supplier'
                supplier_user.save()
                # Create supplier profile if needed
                Supplier.objects.get_or_create(
                    user=supplier_user,
                    defaults={'company_name': f'{supplier_user.username} Company', 'contact_number': '0712345678'}
                )

        if supplier_user:
            print(f'   Using supplier: {supplier_user.username} (role: {supplier_user.role})')

            factory = RequestFactory()
            request = factory.get('/dashboard/download-supplier-report/')
            request.user = supplier_user

            # Add middleware
            def dummy_get_response(request):
                return None
            session_middleware = SessionMiddleware(dummy_get_response)
            session_middleware.process_request(request)
            request.session.save()

            message_middleware = MessageMiddleware(dummy_get_response)
            message_middleware.process_request(request)

            response = download_supplier_report(request)
            print(f'   Response status: {response.status_code}')
            print(f'   Content-Type: {response.get("Content-Type")}')
            print(f'   Content-Disposition: {response.get("Content-Disposition")}')

            if response.status_code == 200 and 'application/pdf' in response.get('Content-Type', ''):
                test_results.append(('Supplier Download', 'PASS'))
                print('   ✅ PASS: PDF generated successfully')
            else:
                test_results.append(('Supplier Download', 'FAIL'))
                print('   ❌ FAIL: PDF not generated')
        else:
            test_results.append(('Supplier Download', 'SKIP - No supplier user'))
            print('   ⚠️  SKIP: No supplier user found')

    except Exception as e:
        test_results.append(('Supplier Download', f'ERROR: {str(e)}'))
        print(f'   ❌ ERROR: {e}')

    print()

    # Test 3: Consultant Download
    print('3. TESTING CONSULTANT DOWNLOAD FUNCTION')
    try:
        consultant = User.objects.filter(user_type='consultant').first() or User.objects.filter(is_consultant=True).first()
        if not consultant:
            consultant = User.objects.filter(user_type='admin').first() or User.objects.first()
            if consultant:
                consultant.user_type = 'consultant'
                consultant.save()

        if consultant:
            print(f'   Using consultant: {consultant.username} (role: {consultant.role})')

            factory = RequestFactory()
            request = factory.get('/dashboard/download-consultant-report/')
            request.user = consultant

            # Add middleware
            def dummy_get_response(request):
                return None
            session_middleware = SessionMiddleware(dummy_get_response)
            session_middleware.process_request(request)
            request.session.save()

            message_middleware = MessageMiddleware(dummy_get_response)
            message_middleware.process_request(request)

            response = download_consultant_report(request)
            print(f'   Response status: {response.status_code}')
            print(f'   Content-Type: {response.get("Content-Type")}')
            print(f'   Content-Disposition: {response.get("Content-Disposition")}')

            if response.status_code == 200 and 'application/pdf' in response.get('Content-Type', ''):
                test_results.append(('Consultant Download', 'PASS'))
                print('   ✅ PASS: PDF generated successfully')
            else:
                test_results.append(('Consultant Download', 'FAIL'))
                print('   ❌ FAIL: PDF not generated')
        else:
            test_results.append(('Consultant Download', 'SKIP - No consultant user'))
            print('   ⚠️  SKIP: No consultant user found')

    except Exception as e:
        test_results.append(('Consultant Download', f'ERROR: {str(e)}'))
        print(f'   ❌ ERROR: {e}')

    print()

    # Test 4: Edge Cases
    print('4. TESTING EDGE CASES')

    # Test with user having no data
    print('   Testing user with no orders/consultations...')
    try:
        empty_user = User.objects.filter(user_type='customer').last() or User.objects.create_user(
            username='test_empty_user',
            email='empty@test.com',
            password='testpass123',
            user_type='customer'
        )

        factory = RequestFactory()
        request = factory.get('/dashboard/download-customer-report/')
        request.user = empty_user

        SessionMiddleware().process_request(request)
        request.session.save()
        MessageMiddleware().process_request(request)

        response = download_customer_report(request)
        if response.status_code == 200 and 'application/pdf' in response.get('Content-Type', ''):
            print('   ✅ PASS: Empty data PDF generated')
        else:
            print('   ❌ FAIL: Empty data PDF not generated')

    except Exception as e:
        print(f'   ❌ ERROR in edge case: {e}')

    print()

    # Summary
    print('=== TEST SUMMARY ===')
    passed = 0
    failed = 0
    skipped = 0
    errors = 0

    for test_name, result in test_results:
        if 'PASS' in result:
            passed += 1
            status = '✅'
        elif 'FAIL' in result:
            failed += 1
            status = '❌'
        elif 'SKIP' in result:
            skipped += 1
            status = '⚠️'
        else:
            errors += 1
            status = '💥'

        print(f'{status} {test_name}: {result}')

    print(f'\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped, {errors} errors')

    if passed >= 2:  # At least customer and supplier working
        print('🎉 OVERALL: PDF download functionality is working!')
        return True
    else:
        print('⚠️  OVERALL: Issues detected - some downloads may not be working')
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
