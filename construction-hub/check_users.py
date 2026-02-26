import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')

# Setup Django
django.setup()

from apps.accounts.models import CustomUser

# Check all users
print("All users and their types:")
users = CustomUser.objects.all()
for user in users:
    print(f"{user.username}: {user.user_type}")

print("\nUsers containing 'munene' or 'vel':")
for user in users:
    if 'munene' in user.username.lower() or 'vel' in user.username.lower():
        print(f"{user.username}: {user.user_type}")

# Update munene to be a customer if not already
try:
    munene_user = CustomUser.objects.get(username__icontains='munene')
    if munene_user.user_type != 'customer':
        munene_user.user_type = 'customer'
        munene_user.save()
        print(f"\nUpdated {munene_user.username} to customer")
    else:
        print(f"\n{munene_user.username} is already a customer")
except CustomUser.DoesNotExist:
    print("\nNo user with 'munene' in username found")
except CustomUser.MultipleObjectsReturned:
    print("\nMultiple users with 'munene' in username found")
