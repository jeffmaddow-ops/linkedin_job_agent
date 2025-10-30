# LinkedIn Job Search Agent

A powerful Python-based agent that searches and scrapes job postings from LinkedIn, with advanced filtering, data export capabilities, and duplicate detection.

## 🎨 New: Material Design 3 Web Interface!

**Now available with a beautiful, modern web interface!**

- **🎨 Material Design 3**: Google's latest design system
- **🌙 Dark/Light Themes**: Automatic theme switching
- **📱 Fully Responsive**: Works on all devices
- **⚡ Real-time Progress**: Live search updates
- **🔍 Advanced Filtering**: Filter by title, company, location, salary
- **💾 Multiple Exports**: CSV, JSON, Excel download

### Quick Start - Web Interface
```bash
# Install dependencies
pip install -r requirements.txt

# Start web server
python web_app.py

# Open browser to http://localhost:5000
```

See [WEB_README.md](WEB_README.md) for detailed web interface documentation.

## Choose Your Interface

### 🎨 Web Interface (Recommended)
**Modern Material Design 3 web application with real-time progress and advanced filtering**

```bash
python web_app.py
# Open http://localhost:5000 in your browser
```

### 💻 Command Line Interface
**Traditional CLI for automation and scripting**

```bash
python job_agent.py "Python developer" --location "San Francisco"
```

---

## Features

- 🔐 **LinkedIn Authentication**: Login with your LinkedIn account for better access to job listings
- 🔍 **Advanced Search**: Search jobs with keywords, location, experience level, job type, and date filters
- 🤖 **Automated Scraping**: Uses Selenium WebDriver for reliable data extraction
- 📊 **Data Export**: Export results to CSV, JSON, or Excel formats
- 🚫 **Duplicate Detection**: Automatically removes duplicate job postings
- 📈 **Analytics**: Get statistics about scraped jobs including top companies and locations
- ⚡ **Rate Limiting**: Built-in delays and rate limiting to avoid being blocked
- 🛡️ **Error Handling**: Robust error handling and graceful shutdowns
- 📱 **CLI Interface**: Easy-to-use command-line interface with comprehensive options
- 🍪 **Session Persistence**: Saves login cookies to avoid repeated logins

## Installation

1. **Clone or download the project:**
   ```bash
   cd linkedin_job_agent
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium browser** (if not already installed):
   - The agent uses Chrome WebDriver which will be automatically downloaded
   - Make sure you have Chrome or Chromium browser installed on your system

4. **Configure LinkedIn credentials (Optional but Recommended):**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your LinkedIn credentials
   # This enables authenticated scraping for better access to job listings
   ```

   Edit `.env` file:
   ```bash
   LINKEDIN_EMAIL=your.email@example.com
   LINKEDIN_PASSWORD=your_password_here
   AUTO_LOGIN=true
   ```

   **Security Notes:**
   - The `.env` file is automatically ignored by git (included in `.gitignore`)
   - Never commit your `.env` file or share it publicly
   - Your credentials are only used locally to login to LinkedIn
   - Session cookies are saved to `linkedin_cookies.json` for reuse

## Quick Start

### Basic Usage

Search for Python developer jobs:
```bash
python job_agent.py "Python developer"
```

### Advanced Search

Search for entry-level data scientist jobs in San Francisco, posted in the past week:
```bash
python job_agent.py "Data scientist" --location "San Francisco, CA" --experience entry --date past-week --max-jobs 50
```

### With Detailed Descriptions

Get full job descriptions (slower but more complete data):
```bash
python job_agent.py "Software engineer" --details --format json --output detailed_jobs.json
```

## Command Line Options

### Required Arguments
- `keywords`: Job search keywords (e.g., "Python developer", "Data scientist")

### Search Filters
- `--location, -l`: Location filter (e.g., "San Francisco", "Remote")
- `--experience, -e`: Experience level (entry, associate, mid-senior, director, executive)
- `--job-type, -t`: Job type (full-time, part-time, contract, temporary, internship)  
- `--date, -d`: Date posted filter (past-24h, past-week, past-month)

### Scraping Options
- `--max-jobs, -n`: Maximum number of jobs to scrape (default: 25)
- `--delay`: Delay between requests in seconds (default: 2.0)
- `--no-headless`: Run browser in visible mode (for debugging)
- `--details`: Fetch detailed job descriptions (slower)

### Output Options
- `--format, -f`: Output format (csv, json, excel) (default: csv)
- `--output, -o`: Custom output filename
- `--no-save`: Don't save results to file
- `--quiet, -q`: Minimal console output

## Examples

### 1. Authenticated Search (Recommended)
```python
# Using the authenticated scraper with .env credentials
from linkedin_scraper_auth import LinkedInJobScraperAuth

scraper = LinkedInJobScraperAuth(headless=False)
if scraper.login_to_linkedin():  # Uses credentials from .env
    search_url = scraper.build_search_url(
        keywords="Senior Software Engineer",
        location="Remote",
        experience_level="mid-senior"
    )
    jobs = scraper.scrape_jobs_authenticated(search_url, max_jobs=25)
scraper.close()
```

### 2. Search for Remote Python Jobs
```bash
python job_agent.py "Python developer" --location "Remote" --job-type full-time --max-jobs 30
```

### 3. Find Recent ML Engineering Positions
```bash
python job_agent.py "Machine Learning Engineer" --date past-week --experience mid-senior --format excel
```

### 4. Get Detailed Job Data for Analysis
```bash
python job_agent.py "Data Analyst" --details --max-jobs 100 --output data_analyst_jobs.csv
```

### 5. Quick Search with Minimal Output
```bash
python job_agent.py "Frontend developer" --quiet --no-save
```

## Output Files

The agent creates a `job_data/` directory and saves files with timestamps:
- `linkedin_jobs_20241030_143022.csv` 
- `linkedin_jobs_20241030_143022.json`
- `linkedin_jobs_20241030_143022.xlsx`

### Data Fields

Each job posting includes:
- **Basic Info**: title, company, location, posted_date, salary
- **URLs**: job_url, company_url  
- **Descriptions**: description_snippet, full_description (with --details)
- **Metadata**: job_id, scraped_at, source
- **Job Details**: employment_type, seniority_level, industry, job_function (with --details)

## Configuration

Edit `config.py` to customize:
- Default scraping delays and limits
- CSS selectors (if LinkedIn changes their layout)
- Chrome browser options
- Rate limiting settings

## Important Notes

### Legal and Ethical Use
- ⚖️ **Respect LinkedIn's Terms of Service**: Use responsibly and in accordance with LinkedIn's robots.txt and terms
- 🚫 **Rate Limiting**: Built-in delays help avoid being blocked - don't disable them
- 👥 **Personal Use**: This tool is intended for personal job searching, not commercial data harvesting

### Technical Considerations
- 🌐 **IP Blocking**: Excessive scraping may result in temporary IP blocks
- 🔄 **Layout Changes**: LinkedIn may update their layout, requiring selector updates
- 💾 **Memory Usage**: Large searches with --details flag use more memory
- ⏱️ **Performance**: Detailed scraping is slower but provides richer data

### Troubleshooting

**Browser Issues:**
- Make sure Chrome/Chromium is installed
- Try running with `--no-headless` flag to see browser actions
- Update Chrome if WebDriver compatibility issues occur

**No Results Found:**
- Check your search keywords and filters
- Try broader search terms
- Verify LinkedIn job search works manually with same parameters

**Rate Limiting:**
- Increase `--delay` parameter (try 3.0 or higher)
- Reduce `--max-jobs` for smaller batches
- Wait before retrying if you get blocked

## Project Structure

```
linkedin_job_agent/
├── job_agent.py              # Main CLI interface
├── linkedin_scraper.py       # Web scraping logic (basic)
├── linkedin_scraper_auth.py  # Web scraping with authentication
├── data_manager.py           # Data storage and export
├── config.py                 # Configuration settings
├── web_app.py                # Flask web interface
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your credentials (gitignored)
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── WEB_README.md             # Web interface documentation
├── web/                      # Web interface assets
└── job_data/                 # Output directory (created automatically)
```

## Dependencies

- **selenium**: Web automation and scraping
- **beautifulsoup4**: HTML parsing  
- **requests**: HTTP client
- **pandas**: Data manipulation and Excel export
- **webdriver-manager**: Automatic WebDriver management
- **lxml**: XML/HTML parser

## Contributing

To extend the agent:

1. **Add new filters**: Update URL building logic in `linkedin_scraper.py`
2. **New export formats**: Add methods to `data_manager.py`
3. **Additional job sites**: Create new scraper classes following the same interface
4. **Enhanced data parsing**: Improve extraction logic for more job details

## License

This project is for educational and personal use. Please respect LinkedIn's terms of service and use responsibly.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your search parameters work on LinkedIn directly
3. Try running with `--no-headless` to debug browser issues
4. Ensure all dependencies are properly installed