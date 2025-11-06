# Environment Variables Setup

## Overview
This project uses a `.env` file to store sensitive configuration like API keys. This keeps secrets out of version control and makes configuration easier.

## Quick Setup

### 1. Copy the example file
```bash
copy .env.example .env
```

### 2. Edit `.env` with your actual keys
Open `.env` and replace the placeholder values:

```env
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Get Your API Keys

#### Google Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste it in `.env`

## Files Explained

| File | Purpose | Committed to Git? |
|------|---------|-------------------|
| `.env` | Your actual secrets | NO (in .gitignore) |
| `.env.example` | Template with placeholders | YES |

## Security Notes

- `.env` is in `.gitignore` - your secrets are safe
- Never commit `.env` to Git
- Always use `.env.example` as a template for new developers
- Never hardcode API keys in source code

## Usage in Code

The project automatically loads environment variables:

```python
from dotenv import load_dotenv
import os

load_dotenv() # Load .env file

# Access variables
api_key = os.getenv('GEMINI_API_KEY')
```

## Available Variables

### Required
- `GEMINI_API_KEY` - Google Gemini AI API key for quiz generation

### Optional (for future use)
- `SECRET_KEY` - Django secret key
- `DEBUG` - Enable/disable debug mode
- `DATABASE_URL` - Database connection string
- `EMAIL_HOST`, `EMAIL_PORT`, etc. - Email configuration

## Dependencies

The project uses `python-dotenv` to load environment variables:

```bash
pip install python-dotenv
```

Already included in `requirements.txt`

## Verification

Test that your `.env` file is loaded correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', 'YES' if os.getenv('GEMINI_API_KEY') else 'NO')"
```

## Troubleshooting

### API Key Not Loading?
1. Make sure `.env` file exists in project root
2. Check the variable name is exactly `GEMINI_API_KEY`
3. No spaces around the `=` sign
4. No quotes needed around the value

### Example `.env` Format
```env
GEMINI_API_KEY=your-actual-api-key-here
DEBUG=True
```

---

**Current Status**: `.env` file configured and working!
