#!/usr/bin/env python
"""
Test script to verify Google login functionality.
Tests include:
- Google SocialApp exists and is configured
- Google login URL is accessible
- Google provider is enabled in settings
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def test_google_social_app():
    """Test that Google SocialApp is properly configured."""
    try:
        site = Site.objects.get_current()
        google_app = SocialApp.objects.filter(provider='google', sites=site).first()

        if not google_app:
            print("✗ Google SocialApp not found")
            return False

        if not google_app.client_id or google_app.client_id == 'your-google-client-id':
            print("✗ Google client_id not configured")
            return False

        if not google_app.secret or google_app.secret == 'your-google-client-secret':
            print("✗ Google secret not configured")
            return False

        print("✓ Google SocialApp is properly configured")
        return True

    except Exception as e:
        print(f"✗ Error checking Google SocialApp: {e}")
        return False

def test_google_login_url():
    """Test that Google login URL is accessible."""
    client = Client()
    try:
        # Test the provider_login_url template tag indirectly
        response = client.get('/accounts/login/')
        if response.status_code != 200:
            print("✗ Login page not accessible")
            return False

        # Check if Google login URL pattern exists
        from django.template import Template, Context
        from allauth.socialaccount.templatetags.socialaccount import provider_login_url

        # This would require more complex testing, but for now check if the template renders
        if 'provider_login_url' in response.content.decode():
            print("✓ Google login URL template tag is present")
            return True
        else:
            print("✗ Google login URL template tag not found")
            return False

    except Exception as e:
        print(f"✗ Error testing Google login URL: {e}")
        return False

def test_google_provider_enabled():
    """Test that Google provider is enabled in Django settings."""
    from django.conf import settings

    if 'allauth.socialaccount.providers.google' in settings.INSTALLED_APPS:
        print("✓ Google provider is enabled in INSTALLED_APPS")
        return True
    else:
        print("✗ Google provider not enabled in INSTALLED_APPS")
        return False

def test_google_login_redirect():
    """Test Google login redirect (mock test)."""
    # This is a basic test - in real scenario would need OAuth flow
    client = Client()
    try:
        # Test if the Google login URL can be constructed
        from allauth.socialaccount.helpers import complete_social_login
        from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

        # Just check if the adapter exists
        adapter = GoogleOAuth2Adapter()
        if adapter:
            print("✓ Google OAuth2 adapter is available")
            return True
        else:
            print("✗ Google OAuth2 adapter not available")
            return False

    except Exception as e:
        print(f"✗ Error testing Google login redirect: {e}")
        return False

def main():
    """Run all Google login tests."""
    print("Testing Google login functionality...\n")

    tests = [
        test_google_provider_enabled,
        test_google_social_app,
        test_google_login_url,
        test_google_login_redirect,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All Google login tests passed!")
        return True
    else:
        print("✗ Some Google login tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
