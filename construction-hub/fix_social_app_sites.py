import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Get or create the site
site, _ = Site.objects.get_or_create(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'Construction Hub'
site.save()

# Update Google social app
google_app = SocialApp.objects.get(provider='google')
google_app.sites.clear()
google_app.sites.add(site)
google_app.save()

# Update Facebook social app if exists
try:
    fb_app = SocialApp.objects.get(provider='facebook')
    fb_app.sites.clear()
    fb_app.sites.add(site)
    fb_app.save()
except SocialApp.DoesNotExist:
    pass

print('Site domain:', Site.objects.get_current().domain)
print('Google app sites:', list(google_app.sites.all()))
print('Done!')
