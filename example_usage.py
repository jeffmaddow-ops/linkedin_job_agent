#!/usr/bin/env python3
"""
Example usage script for LinkedIn Job Search Agent
Demonstrates how to use the agent programmatically
"""

from linkedin_scraper import LinkedInJobScraper
from linkedin_scraper_auth import LinkedInJobScraperAuth
from data_manager import JobDataManager
from job_agent import JobSearchAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_basic_search():
    """Example of basic job search"""
    print("=== Basic Job Search Example ===")
    
    agent = JobSearchAgent()
    
    # Search for Python developer jobs
    jobs = agent.search_jobs(
        keywords="Python developer",
        location="San Francisco, CA", 
        max_jobs=10
    )
    
    if jobs:
        # Save to CSV
        csv_file = agent.save_jobs(jobs, "csv", "python_jobs_example.csv")
        print(f"Saved {len(jobs)} jobs to {csv_file}")
        
        # Display summary
        agent.display_job_summary(jobs)
    
    return jobs


def example_advanced_search():
    """Example of advanced job search with detailed data"""
    print("\n=== Advanced Job Search Example ===")
    
    agent = JobSearchAgent()
    
    # Search for data scientist jobs with detailed descriptions
    jobs = agent.search_jobs(
        keywords="Data scientist",
        location="Remote",
        experience_level="mid-senior",
        job_type="full-time",
        date_posted="past-week",
        max_jobs=5,  # Small number for demo
        get_details=True  # Get full job descriptions
    )
    
    if jobs:
        # Save to JSON for better structure
        json_file = agent.save_jobs(jobs, "json", "data_scientist_jobs_detailed.json")
        print(f"Saved detailed data for {len(jobs)} jobs to {json_file}")
    
    return jobs


def example_data_analysis():
    """Example of analyzing scraped job data"""
    print("\n=== Data Analysis Example ===")
    
    # Create data manager
    data_manager = JobDataManager()
    
    # For this example, let's create some mock data
    sample_jobs = [
        {
            "job_id": "1",
            "title": "Python Developer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "salary": "$120,000 - $160,000",
            "posted_date": "2 days ago"
        },
        {
            "job_id": "2", 
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "Remote",
            "salary": "$130,000 - $180,000", 
            "posted_date": "1 day ago"
        },
        {
            "job_id": "3",
            "title": "Software Engineer",
            "company": "TechCorp",
            "location": "New York, NY",
            "salary": "",
            "posted_date": "3 days ago"
        }
    ]
    
    # Clean the data
    cleaned_jobs = data_manager.clean_job_data(sample_jobs)
    
    # Get statistics
    stats = data_manager.get_job_stats(cleaned_jobs)
    
    print("Job Statistics:")
    print(f"- Total jobs: {stats['total_jobs']}")
    print(f"- Unique companies: {stats['unique_companies']}")
    print(f"- Unique locations: {stats['unique_locations']}")
    print(f"- Jobs with salary: {stats['jobs_with_salary']}")
    
    print("\nTop companies:")
    for company, count in stats['most_common_companies'].items():
        print(f"- {company}: {count} jobs")
    
    return cleaned_jobs


def example_custom_scraper():
    """Example of using the scraper directly with custom parameters"""
    print("\n=== Custom Scraper Example ===")

    # Create scraper with custom settings
    scraper = LinkedInJobScraper(headless=True, delay=3.0)

    try:
        # Build custom search URL
        search_url = scraper.build_search_url(
            keywords="Machine Learning Engineer",
            location="Seattle, WA",
            experience_level="mid-senior",
            date_posted="past-month"
        )

        print(f"Search URL: {search_url}")

        # Scrape jobs (commented out to avoid actual scraping in example)
        # jobs = scraper.scrape_jobs(search_url, max_jobs=5)
        # print(f"Found {len(jobs)} jobs")

        print("(Scraping disabled in example - uncomment to run actual search)")

    finally:
        scraper.close()


def example_authenticated_scraper():
    """Example of using authenticated scraper with credentials from .env"""
    print("\n=== Authenticated Scraper Example ===")

    # Check if credentials are in environment
    has_creds = os.getenv('LINKEDIN_EMAIL') and os.getenv('LINKEDIN_PASSWORD')

    if has_creds:
        print("✅ Found LinkedIn credentials in .env file")
    else:
        print("⚠️ No credentials in .env - will prompt for login")
        print("   To avoid prompts, add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to .env")

    # Create authenticated scraper
    scraper = LinkedInJobScraperAuth(headless=False, delay=2.0)

    try:
        # Login to LinkedIn (will use .env credentials if available)
        if scraper.login_to_linkedin():
            print("✅ Successfully logged in!")

            # Build search URL
            search_url = scraper.build_search_url(
                keywords="Senior Software Engineer",
                location="Remote",
                experience_level="mid-senior",
                job_type="full-time",
                date_posted="past-week"
            )

            # Scrape jobs with authentication
            # Uncomment to run actual search:
            # jobs = scraper.scrape_jobs_authenticated(search_url, max_jobs=10)
            # print(f"\n✅ Found {len(jobs)} jobs!")
            #
            # # Save results
            # data_manager = JobDataManager()
            # data_manager.save_to_csv(jobs, "authenticated_jobs.csv")

            print("(Scraping disabled in example - uncomment to run actual search)")
        else:
            print("❌ Login failed")

    finally:
        # Optional: logout when done
        # scraper.logout()
        scraper.close()


def main():
    """Run all examples"""
    print("LinkedIn Job Search Agent - Usage Examples")
    print("=" * 50)

    # Example 1: Basic search
    jobs1 = example_basic_search()

    # Example 2: Advanced search
    jobs2 = example_advanced_search()

    # Example 3: Data analysis
    jobs3 = example_data_analysis()

    # Example 4: Custom scraper usage
    example_custom_scraper()

    # Example 5: Authenticated scraper (NEW!)
    example_authenticated_scraper()

    print(f"\n=== Examples Complete ===")
    print("Check the job_data/ directory for output files")


if __name__ == "__main__":
    main()