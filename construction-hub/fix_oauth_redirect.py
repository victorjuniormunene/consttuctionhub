"""
Script to fix OAuth redirect URI issues.
Run this script to configure the site and social apps correctly:
    python manage.py shell < fix_oauth_redirect.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Update the site domain to match the redirect URI
site = Site.objects.get_current()
site.domain = '127.0.0.1:8000'
site.name = 'Construction Hub'
site.save()

print(f'Site domain set to: {site.domain}')

# Update Google social app sites
try:
    google_app = SocialApp.objects.get(provider='google')
    google_app.sites.clear()
    google_app.sites.add(site)
    google_app.save()
    print(f'Google app sites: {list(google_app.sites.all())}')
except SocialApp.DoesNotExist:
    print('Google Social App not found! Run create_social_apps.py first.')

# Update Facebook social app sites if exists
try:
    fb_app = SocialApp.objects.get(provider='facebook')
    fb_app.sites.clear()
    fb_app.sites.add(site)
    fb_app.save()
    print(f'Facebook app sites: {list(fb_app.sites.all())}')
except SocialApp.DoesNotExist:
    pass

print('\n=== OAuth Redirect URI Configuration ===')
print('Your app is accessed at: http://127.0.0.1:8000')
print('')
print('IMPORTANT: Add the following redirect URI in Google Cloud Console:')
print('')
print('  http://127.0.0.1:8000/accounts/google/login/callback/')
print('')
print('To add this in Google Cloud Console:')
print('1. Go to https://console.cloud.google.com/')
print('2. Select your project')
print('3. Go to APIs & Services > Credentials')
print('4. Click on your OAuth 2.0 Client ID')
print('5. Under "Authorized redirect URIs", add the URI above')
print('6. Click Save')
print('')
print('Done! Restart your Django server and try logging in again.')
