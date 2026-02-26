"""
Script to create Social Applications for Google and Facebook login.
Run this script to set up social authentication:
    python manage.py shell < create_social_apps.py
"""

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp, SocialToken

# Get the current site
site = Site.objects.get_current()

# Create Google Social App (placeholder credentials - replace with real ones)
google_app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google',
        'client_id': 'YOUR_GOOGLE_CLIENT_ID',
        'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
        'key': '',
    }
)
google_app.sites.add(site)

# Create Facebook Social App (placeholder credentials - replace with real ones)
facebook_app, created = SocialApp.objects.get_or_create(
    provider='facebook',
    defaults={
        'name': 'Facebook',
        'client_id': 'YOUR_FACEBOOK_APP_ID',
        'secret': 'YOUR_FACEBOOK_APP_SECRET',
        'key': '',
    }
)
facebook_app.sites.add(site)

print("Social Applications created successfully!")
print("Note: These are placeholder credentials. You need to:")
print("1. Create a project in Google Cloud Console")
print("2. Create an app in Facebook Developers")
print("3. Update the client_id and secret with real credentials")
print("4. Set up authorized redirect URIs")
