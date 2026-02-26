#!/usr/bin/env python
"""
Test script to verify all dashboard views work correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.dashboard.views import customer_dashboard_view, supplier_dashboard_view, consultant_dashboard_view
from apps.accounts.models import CustomUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

def test_dashboards():
    print("Testing Dashboard Functionality")
    print("=" * 40)

    # Create test users if they don't exist
    User = get_user_model()
    customer_user, created = User.objects.get_or_create(
        username='test_customer',
        defaults={'email': 'customer@test.com', 'user_type': 'customer'}
    )
    supplier_user, created = User.objects.get_or_create(
        username='test_supplier',
        defaults={'email': 'supplier@test.com', 'user_type': 'supplier'}
    )
    consultant_user, created = User.objects.get_or_create(
        username='test_consultant',
        defaults={'email': 'consultant@test.com', 'user_type': 'consultant'}
    )

    factory = RequestFactory()

    def test_dashboard(user, view_func, dashboard_name):
        print(f'\n--- Testing {dashboard_name} Dashboard ---')
        try:
            request = factory.get('/dashboard/')
            request.user = user

            # Add session middleware
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()

            # Add auth middleware
            auth_middleware = AuthenticationMiddleware()
            auth_middleware.process_request(request)

            response = view_func(request)
            print(f'✓ {dashboard_name} dashboard loaded successfully (status: {response.status_code})')
            return True
        except Exception as e:
            print(f'✗ {dashboard_name} dashboard failed: {str(e)}')
            return False

    # Test all dashboards
    results = []
    results.append(test_dashboard(customer_user, customer_dashboard_view, 'Customer'))
    results.append(test_dashboard(supplier_user, supplier_dashboard_view, 'Supplier'))
    results.append(test_dashboard(consultant_user, consultant_dashboard_view, 'Consultant'))

    print(f'\n--- Summary ---')
    print(f'Dashboards tested: {len(results)}')
    print(f'Successful: {sum(results)}')
    print(f'Failed: {len(results) - sum(results)}')

    if all(results):
        print('✓ All dashboard tests passed!')
        return True
    else:
        print('✗ Some dashboard tests failed!')
        return False

if __name__ == '__main__':
    test_dashboards()
