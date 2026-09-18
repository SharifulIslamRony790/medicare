import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

if admin:
    admin.set_password('admin1234')
    admin.save()
    print(f"Password for existing admin '{admin.username}' reset to 'admin1234'")
else:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print("Created new admin user 'admin' with password 'admin1234'")
