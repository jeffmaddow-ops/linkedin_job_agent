import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib


class JobDataManager:
    """
    Handles data storage, export, and duplicate detection for job postings.
    """
    
    def __init__(self, output_dir: str = "job_data"):
        """
        Initialize the data manager.
        
        Args:
            output_dir: Directory to store job data files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.seen_jobs = set()  # Track job IDs to avoid duplicates
        
    def generate_job_hash(self, job_data: Dict) -> str:
        """
        Generate a hash for a job posting to detect duplicates.
        
        Args:
            job_data: Job posting dictionary
            
        Returns:
            MD5 hash string
        """
        # Create a unique identifier from job title, company, and location
        identifier = f"{job_data.get('title', '')}-{job_data.get('company', '')}-{job_data.get('location', '')}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def is_duplicate(self, job_data: Dict) -> bool:
        """
        Check if a job posting is a duplicate.
        
        Args:
            job_data: Job posting dictionary
            
        Returns:
            True if duplicate, False otherwise
        """
        job_hash = self.generate_job_hash(job_data)
        job_id = job_data.get('job_id', '')
        
        # Check both job ID and hash to catch duplicates
        if job_id in self.seen_jobs or job_hash in self.seen_jobs:
            return True
            
        self.seen_jobs.add(job_id)
        self.seen_jobs.add(job_hash)
        return False
    
    def clean_job_data(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicates and clean job data.
        
        Args:
            jobs: List of job posting dictionaries
            
        Returns:
            Cleaned list of unique job postings
        """
        cleaned_jobs = []
        
        for job in jobs:
            if not self.is_duplicate(job):
                # Clean up the job data
                cleaned_job = self.clean_single_job(job)
                cleaned_jobs.append(cleaned_job)
            else:
                print(f"Skipping duplicate job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                
        return cleaned_jobs
    
    def clean_single_job(self, job: Dict) -> Dict:
        """
        Clean and standardize a single job posting.
        
        Args:
            job: Job posting dictionary
            
        Returns:
            Cleaned job dictionary
        """
        cleaned_job = {}
        
        # Standard fields with fallbacks
        cleaned_job['job_id'] = job.get('job_id', '')
        cleaned_job['title'] = job.get('title', '').strip()
        cleaned_job['company'] = job.get('company', '').strip()
        cleaned_job['location'] = job.get('location', '').strip()
        cleaned_job['posted_date'] = job.get('posted_date', '').strip()
        cleaned_job['salary'] = job.get('salary', '').strip()
        cleaned_job['job_url'] = job.get('job_url', '').strip()
        cleaned_job['company_url'] = job.get('company_url', '').strip()
        cleaned_job['description_snippet'] = job.get('description_snippet', '').strip()
        
        # Additional fields from detailed scraping
        cleaned_job['full_description'] = job.get('full_description', '').strip()
        cleaned_job['employment_type'] = job.get('employment_type', '').strip()
        cleaned_job['seniority_level'] = job.get('seniority_level', '').strip()
        cleaned_job['industry'] = job.get('industry', '').strip()
        cleaned_job['job_function'] = job.get('job_function', '').strip()
        
        # Add scraping metadata
        cleaned_job['scraped_at'] = datetime.now().isoformat()
        cleaned_job['source'] = 'LinkedIn'
        
        return cleaned_job
    
    def save_to_csv(self, jobs: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save job data to CSV file.
        
        Args:
            jobs: List of job posting dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.csv"
            
        filepath = self.output_dir / filename
        
        if not jobs:
            print("No jobs to save")
            return str(filepath)
        
        # Get all possible field names
        all_fields = set()
        for job in jobs:
            all_fields.update(job.keys())
            
        fieldnames = sorted(list(all_fields))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(jobs)
            
        print(f"Saved {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def save_to_json(self, jobs: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save job data to JSON file.
        
        Args:
            jobs: List of job posting dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.json"
            
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(jobs, jsonfile, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def save_to_excel(self, jobs: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save job data to Excel file.
        
        Args:
            jobs: List of job posting dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.xlsx"
            
        filepath = self.output_dir / filename
        
        df = pd.DataFrame(jobs)
        df.to_excel(filepath, index=False)
        
        print(f"Saved {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def load_from_json(self, filepath: str) -> List[Dict]:
        """
        Load job data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of job posting dictionaries
        """
        with open(filepath, 'r', encoding='utf-8') as jsonfile:
            jobs = json.load(jsonfile)
        
        print(f"Loaded {len(jobs)} jobs from {filepath}")
        return jobs
    
    def load_from_csv(self, filepath: str) -> List[Dict]:
        """
        Load job data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of job posting dictionaries
        """
        jobs = []
        
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            jobs = list(reader)
        
        print(f"Loaded {len(jobs)} jobs from {filepath}")
        return jobs
    
    def merge_job_data(self, *job_lists: List[Dict]) -> List[Dict]:
        """
        Merge multiple job data lists, removing duplicates.
        
        Args:
            *job_lists: Variable number of job lists to merge
            
        Returns:
            Merged list without duplicates
        """
        # Reset seen jobs for fresh duplicate detection
        self.seen_jobs.clear()
        
        merged_jobs = []
        for job_list in job_lists:
            for job in job_list:
                if not self.is_duplicate(job):
                    merged_jobs.append(job)
        
        print(f"Merged {len(merged_jobs)} unique jobs from {len(job_lists)} lists")
        return merged_jobs
    
    def get_job_stats(self, jobs: List[Dict]) -> Dict:
        """
        Get statistics about the job data.
        
        Args:
            jobs: List of job posting dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not jobs:
            return {}
        
        stats = {
            'total_jobs': len(jobs),
            'unique_companies': len(set(job.get('company', '') for job in jobs if job.get('company'))),
            'unique_locations': len(set(job.get('location', '') for job in jobs if job.get('location'))),
            'jobs_with_salary': len([job for job in jobs if job.get('salary')]),
            'most_common_companies': {},
            'most_common_locations': {},
            'posting_dates': {}
        }
        
        # Count companies
        company_counts = {}
        for job in jobs:
            company = job.get('company', '').strip()
            if company:
                company_counts[company] = company_counts.get(company, 0) + 1
        
        stats['most_common_companies'] = dict(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Count locations
        location_counts = {}
        for job in jobs:
            location = job.get('location', '').strip()
            if location:
                location_counts[location] = location_counts.get(location, 0) + 1
                
        stats['most_common_locations'] = dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Count posting dates
        date_counts = {}
        for job in jobs:
            date = job.get('posted_date', '').strip()
            if date:
                date_counts[date] = date_counts.get(date, 0) + 1
                
        stats['posting_dates'] = dict(sorted(date_counts.items(), key=lambda x: x[1], reverse=True))
        
        return stats