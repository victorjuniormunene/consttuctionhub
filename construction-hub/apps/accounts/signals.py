from django.contrib.auth import get_user_model
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

User = get_user_model()

@receiver(social_account_added)
def set_user_type_for_social_login(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user.user_type:
        user.user_type = 'customer'  # default to customer for social login
        user.save()
