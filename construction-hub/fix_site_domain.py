import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Update the site domain
site = Site.objects.get_current()
site.domain = '127.0.0.1:8000'
site.name = 'Construction Hub'
site.save()

# Verify the social app sites
google_app = SocialApp.objects.get(provider='google')
print('Google app sites:', list(google_app.sites.all()))

# Ensure the site is associated with the social app
google_app.sites.add(site)
print('Updated site to:', site.domain)
print('Done!')
