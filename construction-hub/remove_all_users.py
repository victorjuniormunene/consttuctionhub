import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.models import CustomUser

def remove_all_users():
    """
    Remove all users from the database.
    This will also delete related objects due to CASCADE deletes.
    """
    user_count = CustomUser.objects.count()
    print(f"Found {user_count} users in the database.")

    if user_count > 0:
        CustomUser.objects.all().delete()
        print("All users have been removed from the database.")
    else:
        print("No users found in the database.")

if __name__ == "__main__":
    remove_all_users()
