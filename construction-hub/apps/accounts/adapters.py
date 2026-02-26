from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not user.user_type:
            user.user_type = 'customer'
            user.save()
        return user
    
    def get_app(self, request, provider, **kwargs):
        try:
            return super().get_app(request, provider, **kwargs)
        except SocialApp.DoesNotExist:
            # Return None if no social app is configured
            return None
