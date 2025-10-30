#!/usr/bin/env python3
"""
LinkedIn Job Scraper with Authentication Support
Enhanced version that supports user login for better job access
"""

import time
import json
import os
import re
import html
from typing import List, Dict, Optional
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import getpass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LinkedInJobScraperAuth:
    """
    Enhanced LinkedIn job scraper with authentication support
    """
    
    def __init__(self, headless: bool = False, delay: float = 2.0):
        """
        Initialize the LinkedIn job scraper with auth support.
        
        Args:
            headless: Whether to run browser in headless mode (False for login)
            delay: Delay between requests
        """
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.is_logged_in = False
        self.login_cookies_file = "linkedin_cookies.json"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options for login."""
        chrome_options = Options()

        # Don't use headless mode for login - we need to see the page
        if self.headless and self.is_logged_in:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Use a realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Enable profile to maintain session
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # Fix ChromeDriver path issue on macOS
        try:
            chromedriver_path = ChromeDriverManager().install()

            # If the path is a directory or points to wrong file, find the actual chromedriver
            if os.path.isdir(chromedriver_path) or not chromedriver_path.endswith('chromedriver'):
                # Get the directory containing chromedriver
                driver_dir = os.path.dirname(chromedriver_path) if not os.path.isdir(chromedriver_path) else chromedriver_path

                # Look for the actual chromedriver executable
                potential_chromedriver = os.path.join(driver_dir, 'chromedriver')
                if os.path.isfile(potential_chromedriver) and os.access(potential_chromedriver, os.X_OK):
                    chromedriver_path = potential_chromedriver
                else:
                    # Search all files in directory
                    for filename in os.listdir(driver_dir):
                        if filename == 'chromedriver':
                            potential_path = os.path.join(driver_dir, filename)
                            if os.path.isfile(potential_path):
                                # Make it executable if it isn't
                                os.chmod(potential_path, 0o755)
                                chromedriver_path = potential_path
                                break

            # Verify the path is valid before using it
            if os.path.isfile(chromedriver_path) and os.access(chromedriver_path, os.X_OK):
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Path is invalid, use fallback
                self.driver = webdriver.Chrome(options=chrome_options)

        except Exception as e:
            # Fallback: try without specifying service (uses system Chrome)
            self.driver = webdriver.Chrome(options=chrome_options)

        # Remove webdriver detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def save_cookies(self):
        """Save login cookies to file."""
        if self.driver and self.is_logged_in:
            cookies = self.driver.get_cookies()
            with open(self.login_cookies_file, 'w') as f:
                json.dump(cookies, f)
            print("✅ Login session saved")
    
    def load_cookies(self):
        """Load saved login cookies."""
        if os.path.exists(self.login_cookies_file):
            try:
                with open(self.login_cookies_file, 'r') as f:
                    cookies = json.load(f)
                
                # Go to LinkedIn first to set domain
                self.driver.get("https://www.linkedin.com")
                time.sleep(2)
                
                # Add each cookie
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Failed to add cookie: {e}")
                
                # Refresh to apply cookies
                self.driver.refresh()
                time.sleep(3)
                
                # Check if still logged in
                if self.check_login_status():
                    print("✅ Successfully restored login session")
                    self.is_logged_in = True
                    return True
                else:
                    print("❌ Saved session expired, need to login again")
                    os.remove(self.login_cookies_file)
                    
            except Exception as e:
                print(f"Failed to load cookies: {e}")
                if os.path.exists(self.login_cookies_file):
                    os.remove(self.login_cookies_file)
        
        return False
    
    def check_login_status(self):
        """Check if user is currently logged in."""
        try:
            # Look for profile elements that indicate login
            profile_elements = [
                "nav .global-nav__me",
                "[data-control-name='identity_welcome_message']",
                ".global-nav__me-photo",
                ".feed-identity-module"
            ]
            
            for selector in profile_elements:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        return True
                except:
                    continue
                    
            return False
            
        except Exception:
            return False
    
    def login_to_linkedin(self, email: str = None, password: str = None):
        """
        Login to LinkedIn with user credentials.

        Args:
            email: LinkedIn email (will check .env file, then prompt if not provided)
            password: LinkedIn password (will check .env file, then prompt if not provided)
        """
        if not self.driver:
            self.setup_driver()

        # Try to load existing session first
        if self.load_cookies():
            return True

        print("🔐 LinkedIn Login Required")
        print("This will improve job search results and access to more listings.")
        print()

        # Get credentials from environment variables if not provided
        if not email:
            email = os.getenv('LINKEDIN_EMAIL')
            if email:
                print(f"📧 Using email from .env file: {email}")

        if not password:
            password = os.getenv('LINKEDIN_PASSWORD')
            if password:
                print("🔑 Using password from .env file")

        # Prompt for credentials if still not available
        if not email:
            email = input("Enter your LinkedIn email: ")

        if not password:
            password = getpass.getpass("Enter your LinkedIn password: ")
        
        try:
            # Navigate to LinkedIn login
            print("🌐 Navigating to LinkedIn login...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Find and fill email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            print("⏳ Logging in...")
            time.sleep(5)
            
            # Check for 2FA or captcha
            current_url = self.driver.current_url
            
            if "challenge" in current_url or "checkpoint" in current_url:
                print("🔐 Two-factor authentication or security check detected")
                print("Please complete the verification in the browser window")
                print("Press Enter when you've completed the verification...")
                input()
                
            elif "feed" not in current_url and "in/" not in current_url:
                # Still on login page - might be wrong credentials or captcha
                print("❌ Login may have failed. Please check the browser window.")
                print("Complete any required verification and press Enter to continue...")
                input()
            
            # Wait a bit more and check login status
            time.sleep(3)
            
            if self.check_login_status():
                print("✅ Successfully logged in to LinkedIn!")
                self.is_logged_in = True
                self.save_cookies()
                return True
            else:
                print("❌ Login verification failed. Please try again.")
                return False
                
        except TimeoutException:
            print("❌ Timeout during login process")
            return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def logout(self):
        """Logout from LinkedIn and clear saved session."""
        if self.driver and self.is_logged_in:
            try:
                self.driver.get("https://www.linkedin.com/m/logout/")
                time.sleep(2)
                print("📤 Logged out of LinkedIn")
            except:
                pass
            
            self.is_logged_in = False
            
            # Remove saved cookies
            if os.path.exists(self.login_cookies_file):
                os.remove(self.login_cookies_file)
                print("🗑️ Cleared saved session")
    
    def build_search_url(self, keywords: str, location: str = "", 
                        experience_level: str = "", job_type: str = "", 
                        date_posted: str = "") -> str:
        """Build LinkedIn jobs search URL with parameters."""
        base_url = "https://www.linkedin.com/jobs/search/?"
        
        params = {"keywords": keywords}
        
        if location:
            params["location"] = location
            
        # Experience level mapping
        experience_map = {
            "entry": "1",
            "associate": "2", 
            "mid-senior": "3",
            "director": "4",
            "executive": "5"
        }
        if experience_level and experience_level in experience_map:
            params["f_E"] = experience_map[experience_level]
            
        # Job type mapping
        job_type_map = {
            "full-time": "F",
            "part-time": "P",
            "contract": "C", 
            "temporary": "T",
            "internship": "I"
        }
        if job_type and job_type in job_type_map:
            params["f_JT"] = job_type_map[job_type]
            
        # Date filter mapping
        date_map = {
            "past-24h": "r86400",
            "past-week": "r604800", 
            "past-month": "r2592000"
        }
        if date_posted and date_posted in date_map:
            params["f_TPR"] = date_map[date_posted]
            
        return base_url + urlencode(params)
    
    def scrape_jobs_authenticated(self, search_url: str, max_jobs: int = 25, 
                                require_login: bool = True) -> List[Dict]:
        """
        Scrape job postings with authentication for better access.
        
        Args:
            search_url: LinkedIn jobs search URL
            max_jobs: Maximum number of jobs to scrape
            require_login: Whether to require login before scraping
            
        Returns:
            List of job posting dictionaries
        """
        if not self.driver:
            self.setup_driver()
        
        # Ensure we're logged in if required
        if require_login and not self.is_logged_in:
            print("🔐 Login required for better job access")
            if not self.login_to_linkedin():
                print("⚠️ Continuing without login - results may be limited")
        
        jobs = []
        
        try:
            print(f"🔍 Searching jobs at: {search_url}")
            self.driver.get(search_url)
            time.sleep(self.delay)
            
            # Wait for job results to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card, .jobs-search-results-list"))
                )
            except TimeoutException:
                print("⚠️ No job results found - page may have loaded differently")
                # Try alternative selectors
                job_selectors = [
                    ".job-search-card",
                    "[data-job-id]",
                    ".jobs-search-results__list-item",
                    ".scaffold-layout__list-container li"
                ]
                
                for selector in job_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✅ Found jobs using selector: {selector}")
                            break
                    except:
                        continue
                else:
                    print("❌ Could not find job listings on page")
                    return []
            
            # Scroll to load more jobs
            print("📜 Loading job listings...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            for i in range(5):  # Scroll up to 5 times to load more jobs
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Wait for lazy-loaded content to populate

                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # No more content to load
                    print(f"   Loaded all available jobs after {i + 1} scrolls")
                    break
                last_height = new_height
            
            # Get job cards using multiple selectors
            job_cards = []
            selectors_to_try = [
                # 2024-2025 LinkedIn selectors - try these first
                "li.scaffold-layout__list-item",
                "div.job-card-container",
                "div.job-card-list__entity-lockup",
                "li.jobs-search-results__list-item",
                # Older selectors
                ".job-search-card",
                "[data-job-id]",
                ".jobs-search-results__list-item",
                ".scaffold-layout__list-container li",
                # Fallback - any list item in results
                "ul.scaffold-layout__list-container > li",
                "div[class*='job-card']"
            ]

            for selector in selectors_to_try:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards and len(cards) > 0:
                        job_cards = cards
                        print(f"📋 Found {len(job_cards)} job cards using selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards:
                print("❌ No job cards found")
                # Save page source for debugging
                try:
                    with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("⚠️ Page HTML saved to debug_page_source.html")

                    # Save screenshot if possible
                    try:
                        self.driver.save_screenshot('debug_screenshot.png')
                        print("⚠️ Screenshot saved to debug_screenshot.png")
                    except:
                        pass
                except Exception as e:
                    print(f"⚠️ Could not save debug files: {e}")
                return []

            # Try to extract jobs from JSON first (more reliable)
            print("🔍 Attempting to extract jobs from page JSON data...")
            jobs = self.extract_jobs_from_page_json()

            if jobs:
                print(f"✅ Successfully extracted {len(jobs)} jobs from JSON data!")
            else:
                print("⚠️ JSON extraction returned no jobs")

            # Enrich JSON jobs with data from DOM (especially descriptions)
            print(f"🔄 Enriching {len(jobs)} JSON jobs with DOM data...")
            job_id_to_json = {job.get('job_id'): job for job in jobs if job.get('job_id')}
            enriched_count = 0
            skipped_count = 0
            debug_saved = 0  # Track how many debug files we've saved

            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    # Extract data from card
                    dom_data = self.extract_job_data_enhanced(card)
                    if not dom_data:
                        skipped_count += 1
                        # Save debug HTML for first 3 failed cards only
                        if debug_saved < 3:
                            try:
                                card_html = card.get_attribute('outerHTML')
                                debug_file = f'debug_failed_card_{debug_saved + 1}.html'
                                with open(debug_file, 'w', encoding='utf-8') as f:
                                    f.write(card_html)
                                debug_saved += 1
                            except:
                                pass
                        continue

                    if not dom_data.get('job_id'):
                        continue

                    job_id = dom_data.get('job_id')

                    # If this job was in our JSON results, enrich it
                    if job_id in job_id_to_json:
                        json_job = job_id_to_json[job_id]
                        enriched = False
                        # Add missing fields from DOM
                        if not json_job.get('description_snippet') and dom_data.get('description_snippet'):
                            json_job['description_snippet'] = dom_data.get('description_snippet', '')
                            enriched = True
                        if not json_job.get('posted_date') and dom_data.get('posted_date'):
                            json_job['posted_date'] = dom_data.get('posted_date', '')
                            enriched = True
                        if not json_job.get('salary') and dom_data.get('salary'):
                            json_job['salary'] = dom_data.get('salary', '')
                            enriched = True
                        if enriched:
                            enriched_count += 1
                except Exception as e:
                    skipped_count += 1
                    continue

            if enriched_count > 0:
                print(f"✅ Enriched {enriched_count} jobs with additional data")
            if skipped_count > 0:
                print(f"⚠️ Skipped {skipped_count} unparseable cards")
            if debug_saved > 0:
                print(f"🐛 Saved {debug_saved} sample failed cards for debugging (debug_failed_card_*.html)")

            # If we still don't have enough jobs, supplement with DOM parsing
            if len(jobs) < len(job_cards) and len(jobs) < max_jobs:
                print(f"⚠️ JSON only got {len(jobs)} jobs but {len(job_cards)} cards available. Supplementing with DOM parsing...")

                # Create a set of job IDs we already have
                existing_job_ids = {job.get('job_id') for job in jobs if job.get('job_id')}
                supplemented_count = 0
                failed_count = 0

                # Extract from DOM cards
                for i, card in enumerate(job_cards):
                    if len(jobs) >= max_jobs:
                        break

                    if i > 0 and i % 10 == 0:  # Add delay every 10 jobs
                        time.sleep(self.delay)

                    try:
                        job_data = self.extract_job_data_enhanced(card)

                        # Skip if extraction failed (returned None)
                        if not job_data:
                            failed_count += 1
                            continue

                        # Skip if no job ID
                        if not job_data.get('job_id'):
                            failed_count += 1
                            continue

                        # Skip if we already have this job
                        if job_data.get('job_id') in existing_job_ids:
                            continue

                        # Add new job
                        jobs.append(job_data)
                        existing_job_ids.add(job_data.get('job_id'))
                        supplemented_count += 1
                        print(f"✅ Scraped job {len(jobs)}: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")

                    except Exception as e:
                        failed_count += 1
                        continue

                if supplemented_count > 0:
                    print(f"✅ Added {supplemented_count} additional jobs from DOM parsing")
                if failed_count > 0:
                    print(f"⚠️ Failed to parse {failed_count} cards (skipped)")

            # Final count
            print(f"📊 Total jobs extracted: {len(jobs)}")

            # Limit to max_jobs
            jobs = jobs[:max_jobs]
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
        
        return jobs
    
    def extract_jobs_from_page_json(self) -> List[Dict]:
        """
        Extract job data directly from JSON embedded in LinkedIn's page source.
        This is more reliable than parsing DOM elements.
        """
        try:
            page_source = self.driver.page_source
            jobs = []

            # LinkedIn embeds JSON data in <code> tags
            # Find all code blocks with id containing "bpr-guid"
            code_pattern = r'<code[^>]*id="bpr-guid-[^"]*"[^>]*>(.*?)</code>'
            code_blocks = re.findall(code_pattern, page_source, re.DOTALL)

            for code_block in code_blocks:
                try:
                    # Unescape HTML entities and parse JSON
                    json_str = html.unescape(code_block.strip())
                    data = json.loads(json_str)

                    # Check if this contains job data
                    if 'included' in data:
                        # Parse job posting cards from the "included" array
                        # JobPostingCard objects with JOBS_SEARCH contain the actual job data
                        for item in data.get('included', []):
                            if item.get('$type') == 'com.linkedin.voyager.dash.jobs.JobPostingCard':
                                # Only process JOBS_SEARCH cards (not JOB_DETAILS)
                                entity_urn = item.get('entityUrn', '')
                                if 'JOBS_SEARCH' in entity_urn:
                                    job_data = self._parse_job_from_json(item)
                                    if job_data:
                                        jobs.append(job_data)

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    continue

            return jobs

        except Exception as e:
            print(f"⚠️ Error extracting jobs from JSON: {e}")
            return []

    def _parse_job_from_json(self, job_json: Dict) -> Optional[Dict]:
        """Parse a single job posting from JSON data (JobPostingCard structure)."""
        try:
            job_data = {}

            # Extract job ID from jobPostingUrn
            job_posting_urn = job_json.get('jobPostingUrn', '')
            if job_posting_urn:
                # URN format: "urn:li:fsd_jobPosting:4319940250"
                job_id = job_posting_urn.split(':')[-1] if ':' in job_posting_urn else job_posting_urn
                job_data['job_id'] = job_id
                job_data['job_url'] = f"https://www.linkedin.com/jobs/view/{job_id}"
            else:
                return None

            # Extract title from jobPostingTitle or title.text
            title = job_json.get('jobPostingTitle')
            if not title:
                title_obj = job_json.get('title', {})
                if isinstance(title_obj, dict):
                    title = title_obj.get('text', 'Title not found')
                else:
                    title = 'Title not found'
            job_data['title'] = title

            # Extract company name from primaryDescription.text
            primary_desc = job_json.get('primaryDescription', {})
            if isinstance(primary_desc, dict):
                job_data['company'] = primary_desc.get('text', 'Company not found')
            else:
                job_data['company'] = 'Company not found'

            # Extract location from secondaryDescription.text
            secondary_desc = job_json.get('secondaryDescription', {})
            if isinstance(secondary_desc, dict):
                job_data['location'] = secondary_desc.get('text', 'Location not specified')
            else:
                job_data['location'] = 'Location not specified'

            # Extract company URL from logo (if available)
            logo = job_json.get('logo', {})
            if isinstance(logo, dict):
                action_target = logo.get('actionTarget', '')
                if action_target:
                    job_data['company_url'] = action_target
                else:
                    job_data['company_url'] = ''
            else:
                job_data['company_url'] = ''

            # Default values for fields not in JobPostingCard
            job_data['workplace_type'] = ''
            job_data['posted_date'] = ''
            job_data['description_snippet'] = ''
            job_data['salary'] = ''

            return job_data

        except Exception as e:
            print(f"⚠️ Error parsing job JSON: {e}")
            return None

    def extract_job_data_enhanced(self, job_card) -> Optional[Dict]:
        """Enhanced job data extraction with multiple fallback selectors."""
        try:
            job_data = {}

            # Check if card is empty/placeholder (lazy-loaded cards that haven't loaded yet)
            card_html = job_card.get_attribute('innerHTML')
            if not card_html or len(card_html.strip()) < 50:
                # Empty placeholder card - skip it silently
                return None

            # Job ID - try multiple approaches
            job_id = None
            for attr in ['data-job-id', 'data-entity-urn', 'data-occludable-job-id']:
                job_id = job_card.get_attribute(attr)
                if job_id:
                    break

            # If we have a job ID, use it and create URL
            if job_id:
                job_data['job_id'] = job_id
                job_data['job_url'] = f"https://www.linkedin.com/jobs/view/{job_id}"
            else:
                job_data['job_id'] = f"job_{int(time.time())}"
                job_data['job_url'] = ""

            # Job title and URL - try multiple approaches
            title_selectors = [
                # 2024-2025 LinkedIn selectors
                "a.job-card-list__title",
                ".job-card-container__link.job-card-container__primary-description",
                "a.job-card-container__link",
                ".scaffold-layout__list-item a[href*='/jobs/']",
                # Older selectors
                "h3.base-search-card__title a",
                ".job-search-card__title a",
                "a[data-control-name='job_search_job_title']",
                ".jobs-unified-top-card__job-title a",
                # Generic fallback
                "a[href*='linkedin.com/jobs/view']"
            ]

            title_elem = None
            title_text = None
            job_url = None

            # Try to find any anchor tag with job URL
            for selector in title_selectors:
                try:
                    title_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    if title_elem:
                        job_url = title_elem.get_attribute('href')
                        title_text = title_elem.text.strip()
                        if title_text:
                            break
                except:
                    continue

            # If still no title text, try searching for any text in the card
            if not title_text:
                try:
                    # Try to find h3 or strong tags that might contain title
                    for tag in ['h3', 'strong', 'span.job-card-list__title', '.sr-only']:
                        try:
                            elem = job_card.find_element(By.CSS_SELECTOR, tag)
                            text = elem.text.strip()
                            if text and len(text) > 5:  # Reasonable title length
                                title_text = text
                                break
                        except:
                            continue
                except:
                    pass

            if title_text:
                job_data['title'] = title_text
                # Update URL if we found one from the link, otherwise keep the one from job_id
                if job_url:
                    job_data['job_url'] = job_url
            else:
                # Can't extract essential data - skip this card
                return None
            
            # Company name and URL
            company_selectors = [
                # 2024-2025 LinkedIn selectors
                ".job-card-container__company-name",
                "span.job-card-container__primary-description",
                ".artdeco-entity-lockup__subtitle",
                "a.job-card-container__link--company",
                # Older selectors
                "h4.base-search-card__subtitle a",
                ".job-search-card__subtitle-link",
                "a[data-control-name='job_search_company_name']",
                ".jobs-unified-top-card__company-name a",
                # Fallback
                "h4", "h4 a"
            ]

            company_elem = None
            company_text = None
            company_url = None

            for selector in company_selectors:
                try:
                    company_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    if company_elem:
                        company_text = company_elem.text.strip()
                        company_url = company_elem.get_attribute('href')
                        if company_text:
                            break
                except:
                    continue

            # Fallback: search for any reasonable company name text
            if not company_text:
                try:
                    # Look for divs or spans that might contain company name
                    for tag in ['div.job-card-container__metadata-item', 'span[aria-label*="company"]', 'div h4']:
                        try:
                            elem = job_card.find_element(By.CSS_SELECTOR, tag)
                            text = elem.text.strip()
                            if text and len(text) > 2 and len(text) < 100:  # Reasonable company name length
                                company_text = text
                                break
                        except:
                            continue
                except:
                    pass

            if company_text:
                job_data['company'] = company_text
                job_data['company_url'] = company_url or ""
            else:
                job_data['company'] = "Company not found"
                job_data['company_url'] = ""
            
            # Location
            location_selectors = [
                # 2024-2025 LinkedIn selectors
                ".job-card-container__metadata-item",
                "li.job-card-container__metadata-item",
                "span.job-card-container__metadata-wrapper",
                # Older selectors
                ".job-search-card__location",
                ".jobs-unified-top-card__bullet",
                "[data-test-id='job-location']",
                # Fallback
                "span[class*='location']", "div[class*='location']"
            ]

            location_elem = None
            location_text = None

            for selector in location_selectors:
                try:
                    location_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    if location_elem:
                        location_text = location_elem.text.strip()
                        if location_text:
                            break
                except:
                    continue

            job_data['location'] = location_text if location_text else "Location not specified"
            
            # Posted date
            date_selectors = [
                # 2024-2025 LinkedIn selectors
                "time.job-card-container__listed-time",
                "time[datetime]",
                ".job-card-container__footer-item time",
                # Older selectors
                ".job-search-card__listdate",
                ".jobs-unified-top-card__subtitle-secondary-grouping time",
                "[data-test-id='job-posted-date']",
                # Fallback
                "time", "span[class*='time']"
            ]

            for selector in date_selectors:
                try:
                    date_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_elem.text.strip()
                    if date_text:
                        job_data['posted_date'] = date_text
                        break
                except:
                    continue
            else:
                job_data['posted_date'] = ""

            # Job description snippet
            desc_selectors = [
                # 2024-2025 LinkedIn selectors
                ".job-card-list__entity-lockup",
                "p.job-card-container__job-insight-text",
                ".job-card-container__insights",
                # Older selectors
                ".job-search-card__snippet",
                ".jobs-unified-top-card__job-insight",
                "[data-test-id='job-snippet']",
                # Fallback
                "p", "div[class*='insight']"
            ]

            for selector in desc_selectors:
                try:
                    desc_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    desc_text = desc_elem.text.strip()
                    if desc_text and len(desc_text) > 10:  # Reasonable description length
                        job_data['description_snippet'] = desc_text
                        break
                except:
                    continue
            else:
                job_data['description_snippet'] = ""

            # Salary (if available)
            salary_selectors = [
                # 2024-2025 LinkedIn selectors
                ".job-card-container__metadata-item--salary",
                "span[class*='salary']",
                "div[class*='compensation']",
                # Older selectors
                ".job-search-card__salary-info",
                ".jobs-unified-top-card__job-insight--salary",
                "[data-test-id='job-salary']"
            ]

            for selector in salary_selectors:
                try:
                    salary_elem = job_card.find_element(By.CSS_SELECTOR, selector)
                    salary_text = salary_elem.text.strip()
                    if salary_text and ('$' in salary_text or '£' in salary_text or '€' in salary_text):
                        job_data['salary'] = salary_text
                        break
                except:
                    continue
            else:
                job_data['salary'] = ""
            
            return job_data
            
        except Exception as e:
            print(f"❌ Error extracting job data: {e}")
            return None
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()


# Example usage
if __name__ == "__main__":
    scraper = LinkedInJobScraperAuth(headless=False)
    
    try:
        # Login to LinkedIn
        if scraper.login_to_linkedin():
            # Search for jobs
            search_url = scraper.build_search_url(
                keywords="Python developer",
                location="San Francisco",
                experience_level="mid-senior"
            )
            
            jobs = scraper.scrape_jobs_authenticated(search_url, max_jobs=10)
            
            print(f"\n✅ Found {len(jobs)} jobs!")
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                if job['salary']:
                    print(f"   Salary: {job['salary']}")
        
    finally:
        scraper.close()