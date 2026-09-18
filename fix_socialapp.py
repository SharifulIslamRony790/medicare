import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def create_dummy_social_app():
    print("Creating dummy Google SocialApp to fix login/signup errors...")
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'example.com', 'name': 'example.com'})
    
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google Login (Dummy)',
            'client_id': 'dummy_client_id_change_this_later',
            'secret': 'dummy_secret_change_this_later',
        }
    )
    app.sites.add(site)
    if created:
        print("Success! Dummy Google SocialApp created.")
    else:
        print("Google SocialApp already exists. Added site binding just in case.")

if __name__ == '__main__':
    create_dummy_social_app()
