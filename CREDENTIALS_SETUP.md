# LinkedIn Credentials Setup Guide

This guide explains how to configure LinkedIn authentication for the job scraper.

## Why Use Authentication?

LinkedIn authentication provides several benefits:
- ✅ Better access to job listings
- ✅ More complete job data
- ✅ Reduced rate limiting
- ✅ Access to jobs requiring login
- ✅ Session persistence via cookies

## Quick Setup (5 minutes)

### Step 1: Create Your Credentials File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Add Your LinkedIn Credentials

Edit the `.env` file and add your LinkedIn login information:

```bash
# Your LinkedIn email
LINKEDIN_EMAIL=your.email@example.com

# Your LinkedIn password
LINKEDIN_PASSWORD=your_password_here

# Enable automatic login (optional)
AUTO_LOGIN=true
```

### Step 3: Verify Setup

Run the authenticated scraper example:

```bash
python example_usage.py
```

Or test directly in Python:

```python
from linkedin_scraper_auth import LinkedInJobScraperAuth

scraper = LinkedInJobScraperAuth(headless=False)
if scraper.login_to_linkedin():
    print("✅ Login successful!")
scraper.close()
```

## Security Best Practices

### 🔒 Protecting Your Credentials

1. **Never commit .env to version control**
   - The `.env` file is already in `.gitignore`
   - Always use `.env.example` for templates

2. **Keep credentials local**
   - Your `.env` file should only exist on your local machine
   - Never share your `.env` file with others

3. **Use strong passwords**
   - Consider enabling 2FA on your LinkedIn account
   - The scraper will prompt you to complete 2FA if enabled

4. **Review permissions**
   - The scraper only uses your credentials to login
   - No data is sent anywhere except to LinkedIn
   - Session cookies are saved locally in `linkedin_cookies.json`

### 📂 Files Created

The authentication system creates these local files:

- `.env` - Your credentials (gitignored)
- `linkedin_cookies.json` - Session cookies (gitignored)

Both files are automatically excluded from git.

## How Authentication Works

1. **First Run**:
   - Reads email/password from `.env`
   - Logs into LinkedIn via Selenium
   - Saves session cookies to `linkedin_cookies.json`

2. **Subsequent Runs**:
   - Loads cookies from `linkedin_cookies.json`
   - Skips login if session is still valid
   - Re-authenticates only if session expired

3. **2FA Handling**:
   - If 2FA is enabled, browser window stays open
   - Complete verification in browser
   - Press Enter in terminal when done

## Troubleshooting

### Login Failed

**Problem**: Login fails even with correct credentials

**Solutions**:
- Run with `headless=False` to see the browser
- Check if LinkedIn requires CAPTCHA or 2FA
- Wait for any security challenges to complete
- Press Enter after completing verification

### Session Expired

**Problem**: "Saved session expired" message

**Solutions**:
- Normal behavior - just re-login
- Cookies expire after some time
- Delete `linkedin_cookies.json` to force fresh login

### Credentials Not Found

**Problem**: Script prompts for email/password

**Solutions**:
- Verify `.env` file exists in project root
- Check `.env` has correct variable names:
  - `LINKEDIN_EMAIL=...`
  - `LINKEDIN_PASSWORD=...`
- Ensure no spaces around `=` sign
- File should be named exactly `.env` (not `.env.txt`)

### Two-Factor Authentication

**Problem**: 2FA verification required

**Solutions**:
- This is normal - LinkedIn may require 2FA
- Complete verification in the browser window
- Script will wait for you
- Press Enter after verification completes

## Alternative: Manual Login

If you prefer not to store credentials in `.env`:

```python
from linkedin_scraper_auth import LinkedInJobScraperAuth

scraper = LinkedInJobScraperAuth(headless=False)
# Will prompt for email and password
scraper.login_to_linkedin()
```

The scraper will prompt you for credentials at runtime.

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LINKEDIN_EMAIL` | Yes* | Your LinkedIn email | `user@example.com` |
| `LINKEDIN_PASSWORD` | Yes* | Your LinkedIn password | `your_password` |
| `AUTO_LOGIN` | No | Enable automatic login | `true` or `false` |

*Required only if you want to avoid interactive prompts

## Logging Out

To logout and clear saved session:

```python
from linkedin_scraper_auth import LinkedInJobScraperAuth

scraper = LinkedInJobScraperAuth()
scraper.login_to_linkedin()
# ... do your scraping ...
scraper.logout()  # Clears cookies
scraper.close()
```

Or manually delete `linkedin_cookies.json`.

## Need Help?

1. Check the main [README.md](README.md) for general troubleshooting
2. Run with `headless=False` to see browser actions
3. Verify your credentials work on linkedin.com directly
4. Check that Chrome/Chromium is up to date
