#!/usr/bin/env python
"""
Script to check SocialApp configuration.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')

django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def check_social_apps():
    """Check SocialApp configuration."""
    print("Checking SocialApp configuration...")

    # Get the site
    try:
        site = Site.objects.get(id=1)
        print(f"Site: {site.domain} ({site.name})")
    except Site.DoesNotExist:
        print("Site with id=1 does not exist!")
        return

    # Get all SocialApps
    apps = SocialApp.objects.all()
    print(f"Found {apps.count()} SocialApps:")

    for app in apps:
        sites = app.sites.all()
        site_domains = [s.domain for s in sites]
        print(f"  - {app.provider}: {app.name} (sites: {site_domains})")
        print(f"    client_id: {app.client_id[:10]}..." if app.client_id else "    client_id: None")
        print(f"    secret: {app.secret[:10]}..." if app.secret else "    secret: None")

if __name__ == '__main__':
    check_social_apps()
