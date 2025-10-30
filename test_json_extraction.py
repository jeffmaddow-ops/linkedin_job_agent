#!/usr/bin/env python3
"""
Test script to verify JSON extraction from LinkedIn page
"""

from linkedin_scraper_auth import LinkedInJobScraperAuth
import sys

# Read the debug HTML file
print("Reading debug HTML file...")
with open('debug_page_with_cards.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create a mock scraper to test JSON extraction
class MockDriver:
    def __init__(self, page_source):
        self.page_source = page_source

    def quit(self):
        # Mock quit method to avoid errors during cleanup
        pass

# Create scraper instance
scraper = LinkedInJobScraperAuth(headless=True)
scraper.driver = MockDriver(html_content)

# Try to extract jobs from JSON
print("\n🔍 Attempting to extract jobs from JSON...")
jobs = scraper.extract_jobs_from_page_json()

print(f"\n✅ Extracted {len(jobs)} jobs!\n")

# Display first 5 jobs
for i, job in enumerate(jobs[:5], 1):
    print(f"Job {i}:")
    print(f"  Title: {job.get('title', 'N/A')}")
    print(f"  Company: {job.get('company', 'N/A')}")
    print(f"  Location: {job.get('location', 'N/A')}")
    print(f"  Job ID: {job.get('job_id', 'N/A')}")
    print(f"  URL: {job.get('job_url', 'N/A')}")
    print()

print(f"Total jobs extracted: {len(jobs)}")
