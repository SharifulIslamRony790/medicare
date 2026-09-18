import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

User = get_user_model()

# 1. Create or Update Superuser (Admin)
admin_username = os.getenv('ADMIN_USERNAME', 'ronyadmin')
admin_email = os.getenv('ADMIN_EMAIL', 'ronyislam8121@gmail.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'ronyadmin1234')

try:
    user, created = User.objects.get_or_create(
        username=admin_username,
        defaults={
            'email': admin_email,
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True
        }
    )
    user.set_password(admin_password)
    user.is_superuser = True
    user.is_staff = True
    user.role = 'admin'
    user.save()
    if created:
        print(f"Superuser '{admin_username}' created successfully.")
    else:
        print(f"Superuser '{admin_username}' updated with new password.")
except Exception as e:
    print(f"Failed to setup superuser: {e}")

# 2. Setup Site for Render
site, created = Site.objects.get_or_create(id=1)
site.domain = 'medicare-5eop.onrender.com'
site.name = 'MediCare'
site.save()
print("Site domain updated successfully.")

# 3. Create Google SocialApp
client_id = os.getenv('GOOGLE_CLIENT_ID', 'dummy_client_id_please_change')
secret = os.getenv('GOOGLE_CLIENT_SECRET', 'dummy_secret_please_change')

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
print("Google SocialApp configured successfully (using dummy credentials if missing in env).")
