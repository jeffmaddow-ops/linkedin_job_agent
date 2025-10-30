#!/usr/bin/env python3
"""
LinkedIn Job Search Agent

A command-line tool to search and scrape job postings from LinkedIn.
"""

import argparse
import sys
import time
from typing import List, Dict
import signal

from linkedin_scraper import LinkedInJobScraper
from data_manager import JobDataManager


class JobSearchAgent:
    """
    Main agent class that orchestrates job searching and data management.
    """
    
    def __init__(self):
        self.scraper = None
        self.data_manager = JobDataManager()
        
    def search_jobs(self, keywords: str, location: str = "", 
                   experience_level: str = "", job_type: str = "",
                   date_posted: str = "", max_jobs: int = 25,
                   headless: bool = True, delay: float = 2.0,
                   get_details: bool = False) -> List[Dict]:
        """
        Search for jobs with specified parameters.
        
        Args:
            keywords: Job search keywords
            location: Location filter  
            experience_level: Experience level filter
            job_type: Job type filter
            date_posted: Date posted filter
            max_jobs: Maximum number of jobs to scrape
            headless: Run browser in headless mode
            delay: Delay between requests
            get_details: Whether to fetch detailed job descriptions
            
        Returns:
            List of job posting dictionaries
        """
        print(f"🔍 Searching for '{keywords}' jobs...")
        if location:
            print(f"📍 Location: {location}")
        if experience_level:
            print(f"👔 Experience level: {experience_level}")
        if job_type:
            print(f"⏰ Job type: {job_type}")
        if date_posted:
            print(f"📅 Date posted: {date_posted}")
        print(f"🎯 Max jobs: {max_jobs}")
        print()
        
        # Initialize scraper
        self.scraper = LinkedInJobScraper(headless=headless, delay=delay)
        
        try:
            # Build search URL
            search_url = self.scraper.build_search_url(
                keywords=keywords,
                location=location,
                experience_level=experience_level,
                job_type=job_type,
                date_posted=date_posted
            )
            
            # Scrape jobs
            jobs = self.scraper.scrape_jobs(search_url, max_jobs)
            
            # Get detailed descriptions if requested
            if get_details and jobs:
                print(f"\\n📄 Fetching detailed descriptions for {len(jobs)} jobs...")
                for i, job in enumerate(jobs):
                    if job.get('job_url'):
                        try:
                            details = self.scraper.get_job_details(job['job_url'])
                            job.update(details)
                            print(f"Got details for job {i+1}/{len(jobs)}")
                            
                            # Add delay between detail requests
                            if i < len(jobs) - 1:
                                time.sleep(delay)
                                
                        except Exception as e:
                            print(f"Error getting details for job {i+1}: {e}")
                            continue
            
            # Clean and deduplicate data
            cleaned_jobs = self.data_manager.clean_job_data(jobs)
            
            print(f"\\n✅ Successfully scraped {len(cleaned_jobs)} unique jobs")
            return cleaned_jobs
            
        except KeyboardInterrupt:
            print("\\n⚠️ Search interrupted by user")
            return []
        except Exception as e:
            print(f"\\n❌ Error during job search: {e}")
            return []
        finally:
            if self.scraper:
                self.scraper.close()
    
    def save_jobs(self, jobs: List[Dict], output_format: str = "csv", 
                 filename: str = None) -> str:
        """
        Save jobs to specified format.
        
        Args:
            jobs: List of job dictionaries
            output_format: Output format (csv, json, excel)
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not jobs:
            print("No jobs to save")
            return ""
            
        if output_format.lower() == "csv":
            return self.data_manager.save_to_csv(jobs, filename)
        elif output_format.lower() == "json":
            return self.data_manager.save_to_json(jobs, filename)
        elif output_format.lower() == "excel":
            return self.data_manager.save_to_excel(jobs, filename)
        else:
            print(f"Unsupported output format: {output_format}")
            return ""
    
    def display_job_summary(self, jobs: List[Dict]):
        """
        Display a summary of scraped jobs.
        
        Args:
            jobs: List of job dictionaries
        """
        if not jobs:
            print("No jobs to display")
            return
            
        print(f"\\n📊 Job Search Summary")
        print("=" * 50)
        
        # Get statistics
        stats = self.data_manager.get_job_stats(jobs)
        
        print(f"Total jobs found: {stats['total_jobs']}")
        print(f"Unique companies: {stats['unique_companies']}")
        print(f"Unique locations: {stats['unique_locations']}")
        print(f"Jobs with salary info: {stats['jobs_with_salary']}")
        
        # Top companies
        if stats['most_common_companies']:
            print(f"\\nTop Companies:")
            for company, count in list(stats['most_common_companies'].items())[:5]:
                print(f"  • {company}: {count} jobs")
        
        # Top locations
        if stats['most_common_locations']:
            print(f"\\nTop Locations:")
            for location, count in list(stats['most_common_locations'].items())[:5]:
                print(f"  • {location}: {count} jobs")
        
        # Show first few jobs
        print(f"\\n📝 Sample Jobs:")
        print("-" * 50)
        for i, job in enumerate(jobs[:3]):
            print(f"{i+1}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            if job.get('salary'):
                print(f"   Salary: {job['salary']}")
            print()


def setup_signal_handler(agent):
    """Setup signal handler for graceful shutdown."""
    def signal_handler(sig, frame):
        print('\\n⚠️ Interrupted! Cleaning up...')
        if agent.scraper:
            agent.scraper.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="LinkedIn Job Search Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Python developer" --location "San Francisco" --max-jobs 50
  %(prog)s "Data scientist" --experience entry --job-type full-time --format json
  %(prog)s "Software engineer" --date past-week --details --output my_jobs.csv
        """
    )
    
    # Required arguments
    parser.add_argument("keywords", 
                       help="Job search keywords (e.g. 'Python developer', 'Data scientist')")
    
    # Search filters
    parser.add_argument("--location", "-l", 
                       default="",
                       help="Location filter (e.g. 'San Francisco', 'Remote')")
    
    parser.add_argument("--experience", "-e",
                       choices=["entry", "associate", "mid-senior", "director", "executive"],
                       default="",
                       help="Experience level filter")
    
    parser.add_argument("--job-type", "-t",
                       choices=["full-time", "part-time", "contract", "temporary", "internship"],
                       default="",
                       help="Job type filter")
    
    parser.add_argument("--date", "-d",
                       choices=["past-24h", "past-week", "past-month"],
                       default="",
                       help="Date posted filter")
    
    # Scraping options
    parser.add_argument("--max-jobs", "-n",
                       type=int,
                       default=25,
                       help="Maximum number of jobs to scrape (default: 25)")
    
    parser.add_argument("--delay",
                       type=float,
                       default=2.0,
                       help="Delay between requests in seconds (default: 2.0)")
    
    parser.add_argument("--no-headless",
                       action="store_true",
                       help="Run browser in non-headless mode (visible)")
    
    parser.add_argument("--details",
                       action="store_true",
                       help="Fetch detailed job descriptions (slower)")
    
    # Output options
    parser.add_argument("--format", "-f",
                       choices=["csv", "json", "excel"],
                       default="csv",
                       help="Output format (default: csv)")
    
    parser.add_argument("--output", "-o",
                       help="Output filename (optional)")
    
    parser.add_argument("--no-save",
                       action="store_true",
                       help="Don't save results to file")
    
    parser.add_argument("--quiet", "-q",
                       action="store_true",
                       help="Minimal output")
    
    args = parser.parse_args()
    
    # Create agent
    agent = JobSearchAgent()
    setup_signal_handler(agent)
    
    # Search for jobs
    jobs = agent.search_jobs(
        keywords=args.keywords,
        location=args.location,
        experience_level=args.experience,
        job_type=args.job_type,
        date_posted=args.date,
        max_jobs=args.max_jobs,
        headless=not args.no_headless,
        delay=args.delay,
        get_details=args.details
    )
    
    if not jobs:
        print("No jobs found or search failed")
        return 1
    
    # Display summary
    if not args.quiet:
        agent.display_job_summary(jobs)
    
    # Save results
    if not args.no_save:
        saved_file = agent.save_jobs(jobs, args.format, args.output)
        if saved_file:
            print(f"\\n💾 Results saved to: {saved_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())