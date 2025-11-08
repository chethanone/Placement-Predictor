from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow all Vercel deployment hosts
ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '127.0.0.1', 'localhost']

# Disable CSRF for API testing (enable in production with proper configuration)
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
]

# Static files configuration for Vercel
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
