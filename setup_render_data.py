import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

User = get_user_model()

# 1. Create Superuser (Admin)
admin_username = os.getenv('ADMIN_USERNAME', 'admin')
admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin1234')

if not User.objects.filter(username=admin_username).exists():
    try:
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role='admin'
        )
        print("Superuser created successfully.")
    except Exception as e:
        print(f"Failed to create superuser: {e}")
else:
    print("Superuser already exists.")

# 2. Setup Site for Render
site, created = Site.objects.get_or_create(id=1)
site.domain = 'medicare-5eop.onrender.com'
site.name = 'MediCare'
site.save()
print("Site domain updated successfully.")

# 3. Create Google SocialApp
client_id = os.getenv('GOOGLE_CLIENT_ID')
secret = os.getenv('GOOGLE_CLIENT_SECRET')

if client_id and secret:
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': client_id,
            'secret': secret,
        }
    )
    if not created:
        app.client_id = client_id
        app.secret = secret
        app.save()

    # Add the site to the app
    app.sites.add(site)
    print("Google SocialApp configured successfully.")
else:
    print("Google Client ID or Secret is missing in environment variables. SocialApp skipped.")
