# Security Setup Guide

## Important: Credentials Configuration

This project requires environment variables for sensitive credentials. You must configure these before running the application.

## Required Steps

### 1. Create `.env` File

Copy the example file and add your credentials:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Or manually copy the file
```

### 2. Generate Django Secret Key

**NEVER use the default secret key in production!**

Generate a new secret key:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add it to your `.env` file:
```env
DJANGO_SECRET_KEY=your-generated-secret-key-here
```

### 3. Get Google Gemini API Key

**Required for AI quiz generation**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to `.env`:
```env
GEMINI_API_KEY=AIzaSy...your-key-here
```

### 4. Firebase Configuration (If Using Firebase)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → General
4. Scroll to "Your apps" section
5. Copy the configuration values

Add to `.env`:
```env
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123
FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/
```

### 5. Google Custom Search API (Optional)

**For enhanced quiz study recommendations**

See `docs/GOOGLE_SEARCH_API_SETUP.md` for detailed instructions.

Add to `.env`:
```env
GOOGLE_SEARCH_API_KEY=your-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
```

## Security Checklist

- [ ] Created `.env` file from `.env.example`
- [ ] Generated new Django secret key
- [ ] Added Gemini API key
- [ ] Added Firebase credentials (if using)
- [ ] Verified `.env` is in `.gitignore`
- [ ] Never committed `.env` to git
- [ ] Changed default admin password after first login
- [ ] Set `DEBUG=False` in production

## Files Protected

The following files are configured to **never** be committed:

- `.env` - All environment variables
- `db.sqlite3` - Local database
- `media/` - User-uploaded files
- `firebase_client/firebase-client.js` - Firebase config
- `config/firebase-credentials.json` - Service account keys

## What Was Removed

Previous versions exposed:
- Firebase API keys
- Gemini API keys  
- Django secret key

All exposed credentials have been:
1. Removed from code
2. Moved to environment variables
3. Added to `.gitignore`
4. Documented in this guide

## If You Forked Before Security Fix

**CRITICAL:** If you forked/cloned this repo before the security update:

1. Rotate all API keys immediately:
   - Generate new Firebase API key
   - Generate new Gemini API key
   - Generate new Django secret key

2. Check your fork for exposed credentials:
   ```bash
   git log --all --full-history --source -- '*firebase*' '*config*' '*.env'
   ```

3. If credentials are in history, consider:
   - Deleting and re-forking the repository
   - Or using `git filter-branch` to remove sensitive data

## Production Deployment

### Additional Security Measures:

1. **Set DEBUG=False**:
```env
DEBUG=False
```

2. **Configure ALLOWED_HOSTS**:
```python
# In settings.py
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

3. **Use HTTPS** (always!)

4. **Set secure cookie flags**:
```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

5. **Use PostgreSQL** (not SQLite):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

6. **Keep dependencies updated**:
```bash
pip install --upgrade -r requirements.txt
```

## Getting Help

- **Django Security**: https://docs.djangoproject.com/en/stable/topics/security/
- **Firebase Security**: https://firebase.google.com/docs/rules
- **Environment Variables**: See `docs/ENV_SETUP.md`

## Quick Start After Setup

Once you've configured your `.env` file:

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

---

**Last Updated:** November 6, 2025  
**Status:** All security issues resolved
