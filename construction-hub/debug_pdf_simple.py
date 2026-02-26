import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.dashboard.views import download_customer_report, download_supplier_report, download_consultant_report
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

User = get_user_model()

print('=== PDF DOWNLOAD DEBUG TEST ===\n')

# Get a user to test with
user = User.objects.first()
if not user:
    print('No users found in database')
    exit()

print(f'Testing with user: {user.username} (role: {getattr(user, "role", "None")})')

# Test each function
functions = [
    ('Customer Report', download_customer_report),
    ('Supplier Report', download_supplier_report),
    ('Consultant Report', download_consultant_report)
]

for name, func in functions:
    try:
        factory = RequestFactory()
        request = factory.get(f'/dashboard/download-{name.lower().split()[0]}-report/')
        request.user = user

        # Add middleware properly
        def dummy_get_response(request):
            return None

        session_middleware = SessionMiddleware(dummy_get_response)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(dummy_get_response)
        message_middleware.process_request(request)

        response = func(request)
        print(f'{name}: Status {response.status_code}, Content-Type: {response.get("Content-Type")}')

        if response.status_code == 200 and 'application/pdf' in response.get('Content-Type', ''):
            print(f'  ✅ {name} generated successfully')
        else:
            print(f'  ❌ {name} failed - {response.content.decode() if hasattr(response, "content") else "No content"}')

    except Exception as e:
        print(f'{name}: ERROR - {e}')

print('\n=== DEBUG COMPLETE ===')
