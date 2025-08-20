import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localloom.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'ogarthomas7@gmail.com')
SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '091599@localloom')

if not User.objects.filter(email=SUPERUSER_EMAIL).exists():
    User.objects.create_superuser(email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD)
    print("Superuser created.")
else:
    print("Superuser already exists.")