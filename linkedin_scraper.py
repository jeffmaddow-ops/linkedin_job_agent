import time
import json
import csv
import os
from typing import List, Dict, Optional
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class LinkedInJobScraper:
    """
    A web scraper for LinkedIn job postings that handles search, extraction, and data parsing.
    """
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        Initialize the LinkedIn job scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            delay: Delay between requests to avoid being blocked
        """
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.jobs_data = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

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

        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def build_search_url(self, keywords: str, location: str = "", 
                        experience_level: str = "", job_type: str = "", 
                        date_posted: str = "") -> str:
        """
        Build LinkedIn jobs search URL with parameters.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            experience_level: Experience level (entry, associate, mid-senior, director, executive)
            job_type: Job type (full-time, part-time, contract, temporary, internship)
            date_posted: Date posted filter (past-24h, past-week, past-month)
            
        Returns:
            Complete LinkedIn jobs search URL
        """
        base_url = "https://www.linkedin.com/jobs/search/?"
        
        params = {"keywords": keywords}
        
        if location:
            params["location"] = location
            
        # Map experience levels to LinkedIn's filter values
        experience_map = {
            "entry": "1",
            "associate": "2", 
            "mid-senior": "3",
            "director": "4",
            "executive": "5"
        }
        if experience_level and experience_level in experience_map:
            params["f_E"] = experience_map[experience_level]
            
        # Map job types to LinkedIn's filter values  
        job_type_map = {
            "full-time": "F",
            "part-time": "P",
            "contract": "C", 
            "temporary": "T",
            "internship": "I"
        }
        if job_type and job_type in job_type_map:
            params["f_JT"] = job_type_map[job_type]
            
        # Map date filters
        date_map = {
            "past-24h": "r86400",
            "past-week": "r604800", 
            "past-month": "r2592000"
        }
        if date_posted and date_posted in date_map:
            params["f_TPR"] = date_map[date_posted]
            
        return base_url + urlencode(params)
    
    def scrape_jobs(self, search_url: str, max_jobs: int = 25) -> List[Dict]:
        """
        Scrape job postings from LinkedIn search results.
        
        Args:
            search_url: LinkedIn jobs search URL
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            List of job posting dictionaries
        """
        if not self.driver:
            self.setup_driver()
            
        jobs = []
        
        try:
            print(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            time.sleep(self.delay)
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-job-id]"))
            )
            
            # Get job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-job-id]")
            
            for i, card in enumerate(job_cards[:max_jobs]):
                if i > 0 and i % 5 == 0:  # Add delay every 5 jobs
                    time.sleep(self.delay)
                    
                try:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                        print(f"Scraped job {len(jobs)}: {job_data['title']} at {job_data['company']}")
                        
                except Exception as e:
                    print(f"Error extracting job data from card {i}: {e}")
                    continue
                    
        except TimeoutException:
            print("Timeout waiting for job results to load")
        except Exception as e:
            print(f"Error during scraping: {e}")
            
        return jobs
    
    def extract_job_data(self, job_card) -> Optional[Dict]:
        """
        Extract job information from a job card element.
        
        Args:
            job_card: Selenium WebElement for the job card
            
        Returns:
            Dictionary containing job data or None if extraction fails
        """
        try:
            job_data = {}
            
            # Job ID
            job_data['job_id'] = job_card.get_attribute('data-job-id')
            
            # Job title
            title_elem = job_card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title a")
            job_data['title'] = title_elem.text.strip() if title_elem else ""
            job_data['job_url'] = title_elem.get_attribute('href') if title_elem else ""
            
            # Company name
            company_elem = job_card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a")
            job_data['company'] = company_elem.text.strip() if company_elem else ""
            job_data['company_url'] = company_elem.get_attribute('href') if company_elem else ""
            
            # Location
            location_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
            job_data['location'] = location_elem.text.strip() if location_elem else ""
            
            # Posted date
            try:
                date_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                job_data['posted_date'] = date_elem.text.strip() if date_elem else ""
            except NoSuchElementException:
                job_data['posted_date'] = ""
            
            # Job description snippet
            try:
                desc_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__snippet")
                job_data['description_snippet'] = desc_elem.text.strip() if desc_elem else ""
            except NoSuchElementException:
                job_data['description_snippet'] = ""
            
            # Salary (if available)
            try:
                salary_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__salary-info")
                job_data['salary'] = salary_elem.text.strip() if salary_elem else ""
            except NoSuchElementException:
                job_data['salary'] = ""
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information by visiting the job posting page.
        
        Args:
            job_url: URL of the specific job posting
            
        Returns:
            Dictionary with detailed job information
        """
        details = {}
        
        try:
            self.driver.get(job_url)
            time.sleep(self.delay)
            
            # Wait for job details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".description__text"))
            )
            
            # Full job description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".description__text")
                details['full_description'] = desc_elem.text.strip() if desc_elem else ""
            except NoSuchElementException:
                details['full_description'] = ""
            
            # Job criteria (employment type, seniority level, etc.)
            try:
                criteria_items = self.driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-item")
                for item in criteria_items:
                    key_elem = item.find_element(By.CSS_SELECTOR, ".description__job-criteria-subheader")
                    value_elem = item.find_element(By.CSS_SELECTOR, ".description__job-criteria-text")
                    
                    if key_elem and value_elem:
                        key = key_elem.text.strip().lower().replace(" ", "_")
                        value = value_elem.text.strip()
                        details[key] = value
                        
            except NoSuchElementException:
                pass
            
        except Exception as e:
            print(f"Error getting job details: {e}")
            
        return details
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            
    def __del__(self):
        """Cleanup WebDriver on object destruction."""
        self.close()