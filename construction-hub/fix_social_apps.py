#!/usr/bin/env python
"""
Script to fix SocialApp site associations.
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

def fix_social_apps():
    """Fix SocialApp site associations."""

    # Get or create the site
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={'domain': '127.0.0.1:8000', 'name': 'Construction Hub'}
    )

    # Get all SocialApps and associate them with the site
    apps = SocialApp.objects.all()
    for app in apps:
        if not app.sites.filter(id=site.id).exists():
            app.sites.add(site)
            print(f"Added site to {app.provider} app")
        else:
            print(f"{app.provider} app already associated with site")

    print("SocialApp site associations fixed!")

if __name__ == '__main__':
    fix_social_apps()
