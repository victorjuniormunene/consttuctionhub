from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Supplier


@receiver(post_save, sender=User)
def create_supplier_for_user(sender, instance, created, **kwargs):
    """Automatically create a Supplier record when a new User with user_type='supplier' is created.

    Note: This creates a minimal Supplier using username as company_name and
    empty strings for location and contact_number. Only for supplier users.
    """
    if created and hasattr(instance, 'user_type') and instance.user_type == 'supplier':
        try:
            Supplier.objects.create(user=instance, company_name=instance.username, location='', contact_number='')
        except Exception:
            # avoid breaking user creation if Supplier model constraints change
            pass
