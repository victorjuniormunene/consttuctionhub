#!/usr/bin/env python
"""
Script to update the Google SocialApp with real client ID and secret.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')

django.setup()

from allauth.socialaccount.models import SocialApp

def update_google_app():
    """Update Google SocialApp with real credentials."""

    try:
        google_app = SocialApp.objects.get(provider='google')
        # IMPORTANT: Replace these with your actual Google OAuth credentials
        # Do not commit actual secrets to version control
        google_app.client_id = 'YOUR_GOOGLE_CLIENT_ID_HERE'
        google_app.secret = 'YOUR_GOOGLE_CLIENT_SECRET_HERE'
        google_app.save()
        print("Google SocialApp updated successfully!")
        print(f"Client ID: {google_app.client_id}")
        print("Secret: [HIDDEN]")
    except SocialApp.DoesNotExist:
        print("Google SocialApp not found. Run create_social_apps.py first.")
    except Exception as e:
        print(f"Error updating Google app: {e}")

if __name__ == '__main__':
    update_google_app()
