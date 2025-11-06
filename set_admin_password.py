import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_project.settings')
django.setup()

from django.contrib.auth.models import User

# Set admin password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print(' Admin password set successfully!')
    print('\n Django Admin Access:')
    print('URL: http://127.0.0.1:8000/admin/')
    print('Username: admin')
    print('Password: admin123')
except User.DoesNotExist:
    print(' Admin user not found')
