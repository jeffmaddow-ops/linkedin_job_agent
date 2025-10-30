"""
Configuration settings for LinkedIn Job Agent
"""

# Default scraping settings
DEFAULT_DELAY = 2.0  # Delay between requests in seconds
DEFAULT_MAX_JOBS = 25
DEFAULT_HEADLESS = True
DEFAULT_OUTPUT_FORMAT = "csv"

# LinkedIn URL and selectors (may need updates if LinkedIn changes their site)
LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs/search/?"

# CSS selectors for job data extraction
JOB_SELECTORS = {
    'job_cards': '[data-job-id]',
    'title': 'h3.base-search-card__title a',
    'company': 'h4.base-search-card__subtitle a',
    'location': '.job-search-card__location',
    'posted_date': '.job-search-card__listdate',
    'description_snippet': '.job-search-card__snippet',
    'salary': '.job-search-card__salary-info',
    'full_description': '.description__text',
    'job_criteria': '.description__job-criteria-item',
    'criteria_header': '.description__job-criteria-subheader',
    'criteria_text': '.description__job-criteria-text'
}

# Experience level mapping
EXPERIENCE_LEVELS = {
    "entry": "1",
    "associate": "2", 
    "mid-senior": "3",
    "director": "4",
    "executive": "5"
}

# Job type mapping
JOB_TYPES = {
    "full-time": "F",
    "part-time": "P",
    "contract": "C", 
    "temporary": "T",
    "internship": "I"
}

# Date filter mapping
DATE_FILTERS = {
    "past-24h": "r86400",
    "past-week": "r604800", 
    "past-month": "r2592000"
}

# Chrome browser options
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Rate limiting settings
RATE_LIMIT_DELAY = 2.0  # Minimum delay between requests
BATCH_DELAY = 5  # Delay every N jobs to avoid rate limiting
BATCH_SIZE = 5  # Number of jobs to process before adding batch delay

# Output settings
DEFAULT_OUTPUT_DIR = "job_data"
SUPPORTED_FORMATS = ["csv", "json", "excel"]

# Error handling
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # Delay before retrying failed requests