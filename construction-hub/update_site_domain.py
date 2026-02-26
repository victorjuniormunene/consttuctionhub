#!/usr/bin/env python
"""
Script to update the Django site domain for production/ngrok deployment.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')

django.setup()

from django.contrib.sites.models import Site

def update_site_domain():
    """Update the site domain to match the ngrok URL."""

    site = Site.objects.get(id=1)
    site.domain = 'latina-subtruncate-haughtily.ngrok-free.dev'
    site.name = 'Construction Hub'
    site.save()

    print(f"Site domain updated to: {site.domain}")
    print("This will fix the redirect URI for Google OAuth.")

if __name__ == '__main__':
    update_site_domain()
