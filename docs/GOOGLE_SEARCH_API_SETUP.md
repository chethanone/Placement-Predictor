# Google Custom Search API Setup Guide

## Overview
This guide will help you set up Google Custom Search API to enable AI-powered study resource recommendations in the quiz results.

## Why Do We Need This?
When students complete a quiz and score below 90%, the system automatically:
1. Identifies their weak areas (question types with <60% accuracy)
2. Uses Google Gemini AI to generate study recommendations
3. Uses Google Custom Search API to find relevant educational resources
4. Displays clickable links to articles, tutorials, and courses

**Without the API:** Generic search links are shown instead of curated resources.

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name: "Placement-Predictor-Quiz" (or your choice)
5. Click "CREATE"
6. Wait for project creation (takes a few seconds)

---

## Step 2: Enable Custom Search API

1. In Google Cloud Console, go to [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Custom Search API"
3. Click on "Custom Search API" from results
4. Click "ENABLE" button
5. Wait for API to be enabled

---

## Step 3: Create API Key

1. Go to [API Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "CREATE CREDENTIALS" button
3. Select "API key" from dropdown
4. Copy the generated API key (it will look like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
5. (Optional) Click "RESTRICT KEY" to limit usage:
- Under "API restrictions", select "Restrict key"
- Check only "Custom Search API"
- Click "SAVE"

**Save this API key** - you'll add it to `.env` file.

---

## Step 4: Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" or "Create a new search engine"
3. Fill in the form:
- **Sites to search:** Enter `*` (to search entire web)
- **Language:** English (or your preference)
- **Search engine name:** "Educational Resources Search"
4. Click "CREATE"
5. You'll see a success message with your Search Engine ID
6. Click "Customize" next to your search engine
7. **Copy the Search Engine ID** (format: `xxxxxxxxxxxxxxxxx:xxxxxxxxx`)

---

## Step 5: Configure Search Engine Settings

1. On the search engine customization page:
- **Search the entire web:** Turn ON (toggle to enabled)
- **Image search:** Turn OFF (we only need text results)
- **Safe search:** Turn ON (filter inappropriate content)
2. Click "Save" at the bottom

**Optional - Prioritize Educational Sites:**
1. In "Sites to search" section, click "Add"
2. Add these educational domains (one per line):
```
*.edu
*.org
stackoverflow.com
github.com
medium.com
towards datascience.com
w3schools.com
mdn web docs
```
3. Set these to "Emphasize" (not "Exclusively search")
4. Click "Update"

---

## Step 6: Update .env File

1. Open your `.env` file in the project root
2. Find these lines:
```env
GOOGLE_SEARCH_API_KEY=your-google-search-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
```
3. Replace with your actual values:
```env
GOOGLE_SEARCH_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=xxxxxxxxxxxxxxxxx:xxxxxxxxx
```
4. Save the file

---

## Step 7: Install Required Package

If you haven't already installed the Google API client:

```bash
.venv\Scripts\python.exe -m pip install google-api-python-client
```

Or update from requirements.txt:
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Step 8: Test the Integration

1. **Restart your Django server** (if running):
- Press `Ctrl+C` in terminal
- Run: `.venv\Scripts\python.exe manage.py runserver`

2. **Take a quiz:**
- Upload a PDF/PPT
- Generate quiz
- Answer questions (try to get some wrong to trigger recommendations)
- Submit quiz

3. **Check results page:**
- You should see "AI-Powered Study Recommendations" section
- Resources should have real titles and URLs (not generic Google search links)
- Each resource should show:
- Title from actual webpage
- Domain name
- Preview snippet

---

## Troubleshooting

### Error: "API key not valid"
**Cause:** Invalid API key or API not enabled
**Fix:**
- Double-check API key in `.env` matches Google Cloud Console
- Ensure Custom Search API is enabled in your project
- Wait a few minutes for changes to propagate

### Error: "Invalid CX"
**Cause:** Search Engine ID is incorrect
**Fix:**
- Verify Search Engine ID in `.env` matches Programmable Search Engine console
- Make sure ID includes the colon (e.g., `xxxxx:xxxxx`)

### No recommendations showing
**Cause:** Score is too high (≥90%) or no weak areas detected
**Fix:**
- Intentionally answer some questions wrong to get <90%
- System only shows recommendations when score is below 90%

### Generic search links instead of real resources
**Cause:** API keys not configured properly
**Fix:**
- Check `.env` file has correct values
- Restart Django server after updating `.env`
- Check terminal for error messages

### Error: "Quota exceeded"
**Cause:** Free tier limit reached (100 queries/day)
**Fix:**
- Wait until next day for quota reset
- Or upgrade to paid plan in Google Cloud Console
- Monitor usage at: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

---

## API Usage Limits

### Free Tier:
- **100 queries per day**
- **No cost**
- **10 results per query**

### How We Use It:
- Each quiz result generates 1-3 queries depending on weak areas
- Lower scores = more queries (more recommendations needed)
- Example:
- 85% score, 1 weak area: 1-2 queries
- 50% score, 3 weak areas: 6-9 queries

### To Monitor Usage:
1. Go to [Google Cloud Console - Quotas](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas)
2. View "Queries per day" usage
3. Set up alerts if approaching limit

---

## Cost Information

### Free Tier:
- First 100 queries/day: **FREE**

### Paid Tier (if you need more):
- $5 per 1,000 queries
- Billed monthly
- Only charged for queries beyond 100/day

**Example Costs:**
- 150 queries/day = 50 paid queries = **$0.25/day** = ~$7.50/month
- 500 queries/day = 400 paid queries = **$2/day** = ~$60/month

---

## Alternative: Without API (Fallback Mode)

If you don't want to set up the API, the system will still work:

**What happens:**
- Generic Google search links are shown
- Format: `https://www.google.com/search?q=your+search+query`
- Students can click links to search manually
- No curated resource titles/snippets

**To use fallback mode:**
- Simply don't add API keys to `.env`
- Or leave them as placeholder values
- System automatically detects missing keys

---

## Security Best Practices

1. **Never commit `.env` to Git:**
- Already in `.gitignore`
- Double-check before pushing code

2. **Restrict API key usage:**
- In Google Cloud Console, restrict to Custom Search API only
- Add HTTP referrer restrictions if deploying to web

3. **Monitor API usage:**
- Set up billing alerts
- Review usage regularly
- Disable API key if suspicious activity

4. **Rotate keys periodically:**
- Generate new API key every 3-6 months
- Delete old keys
- Update `.env` with new key

---

## Testing Without API Key

If you want to test the system without setting up the API:

1. The system will use fallback mode
2. You'll see generic Google search links
3. All other features work normally:
- AI recommendations still generate (using Gemini)
- Performance analysis works
- Weak areas identified correctly
- Only resource discovery is limited

---

## Additional Resources

- [Custom Search JSON API Documentation](https://developers.google.com/custom-search/v1/overview)
- [Python Client Library Guide](https://github.com/googleapis/google-api-python-client)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Programmable Search Engine](https://programmablesearchengine.google.com/)

---

## Support

If you encounter issues:
1. Check terminal output for error messages
2. Verify API keys in `.env` file
3. Ensure Django server was restarted after updating `.env`
4. Check Google Cloud Console for API status
5. Review API quota limits

---

**Last Updated:** November 3, 2025
**API Version:** Custom Search API v1
**Client Library:** google-api-python-client ≥2.100.0

**Status:** Optional but recommended for best user experience
