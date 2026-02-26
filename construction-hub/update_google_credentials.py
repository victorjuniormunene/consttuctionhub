import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

# Update Google credentials
# IMPORTANT: Replace these with your actual Google OAuth credentials
# Do not commit actual secrets to version control
app = SocialApp.objects.get(provider='google')
app.client_id = 'YOUR_GOOGLE_CLIENT_ID_HERE'
app.secret = 'YOUR_GOOGLE_CLIENT_SECRET_HERE'
app.save()

print('Google credentials updated successfully!')
