#!/usr/bin/env python3
"""
Flask Web Application for LinkedIn Job Search Agent
Material Design 3 frontend interface
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our existing job agent modules
from linkedin_scraper_auth import LinkedInJobScraperAuth
from data_manager import JobDataManager


app = Flask(__name__,
           template_folder='web/templates',
           static_folder='web/static')

# Secret key for sessions (use environment variable in production)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Global variables for job search state
current_search = {
    'status': 'idle',  # idle, searching, completed, error
    'progress': 0,
    'jobs_found': 0,
    'message': '',
    'jobs': [],
    'search_id': None
}

# Global variable for scraper instance (persists across requests)
scraper_instance = None
scraper_lock = threading.Lock()

search_lock = threading.Lock()


@app.route('/')
def index():
    """Main page with job search interface"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint to start job search"""
    global current_search
    
    with search_lock:
        if current_search['status'] == 'searching':
            return jsonify({'error': 'Search already in progress'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('keywords'):
        return jsonify({'error': 'Keywords are required'}), 400
    
    # Generate search ID
    search_id = f"search_{int(time.time())}"
    
    # Reset search state
    with search_lock:
        current_search.update({
            'status': 'searching',
            'progress': 0,
            'jobs_found': 0,
            'message': 'Starting job search...',
            'jobs': [],
            'search_id': search_id
        })
    
    # Start search in background thread
    search_thread = threading.Thread(
        target=background_search,
        args=(data, search_id)
    )
    search_thread.daemon = True
    search_thread.start()
    
    return jsonify({
        'success': True,
        'search_id': search_id,
        'message': 'Job search started'
    })


@app.route('/api/status')
def api_status():
    """Get current search status"""
    with search_lock:
        return jsonify(current_search.copy())


@app.route('/api/results')
def api_results():
    """Get search results"""
    with search_lock:
        return jsonify({
            'jobs': current_search['jobs'],
            'count': len(current_search['jobs']),
            'status': current_search['status']
        })


@app.route('/api/export/<format>')
def api_export(format):
    """Export job results to file"""
    if format not in ['csv', 'json', 'excel']:
        return jsonify({'error': 'Invalid format'}), 400
    
    with search_lock:
        jobs = current_search['jobs'].copy()
    
    if not jobs:
        return jsonify({'error': 'No jobs to export'}), 400
    
    try:
        data_manager = JobDataManager()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_jobs_export_{timestamp}"
        
        if format == 'csv':
            filepath = data_manager.save_to_csv(jobs, f"{filename}.csv")
        elif format == 'json':
            filepath = data_manager.save_to_json(jobs, f"{filename}.json")
        elif format == 'excel':
            filepath = data_manager.save_to_excel(jobs, f"{filename}.xlsx")
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.route('/api/clear')
def api_clear():
    """Clear current search results"""
    global current_search

    with search_lock:
        if current_search['status'] == 'searching':
            return jsonify({'error': 'Cannot clear during active search'}), 400

        current_search.update({
            'status': 'idle',
            'progress': 0,
            'jobs_found': 0,
            'message': '',
            'jobs': [],
            'search_id': None
        })

    return jsonify({'success': True, 'message': 'Results cleared'})


@app.route('/api/auth/status')
def api_auth_status():
    """Get current authentication status"""
    global scraper_instance

    with scraper_lock:
        is_logged_in = scraper_instance is not None and scraper_instance.is_logged_in

        # Check if credentials are available in env
        has_env_creds = bool(os.getenv('LINKEDIN_EMAIL') and os.getenv('LINKEDIN_PASSWORD'))

        return jsonify({
            'logged_in': is_logged_in,
            'has_env_credentials': has_env_creds,
            'auto_login_enabled': os.getenv('AUTO_LOGIN', 'false').lower() == 'true'
        })


@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    """Login to LinkedIn with provided credentials"""
    global scraper_instance

    data = request.get_json()

    # Get credentials from request or environment
    email = data.get('email') or os.getenv('LINKEDIN_EMAIL')
    password = data.get('password') or os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        with scraper_lock:
            # Create scraper if doesn't exist
            if scraper_instance is None:
                scraper_instance = LinkedInJobScraperAuth(headless=True, delay=2.0)

            # Attempt login
            success = scraper_instance.login_to_linkedin(email=email, password=password)

            if success:
                session['authenticated'] = True
                return jsonify({
                    'success': True,
                    'message': 'Successfully logged in to LinkedIn'
                })
            else:
                return jsonify({
                    'error': 'Login failed. Please check your credentials.'
                }), 401

    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    """Logout from LinkedIn"""
    global scraper_instance

    try:
        with scraper_lock:
            if scraper_instance is not None:
                scraper_instance.logout()
                scraper_instance.close()
                scraper_instance = None

            session.pop('authenticated', None)

        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        })

    except Exception as e:
        return jsonify({'error': f'Logout error: {str(e)}'}), 500


@app.route('/api/auth/use-env', methods=['POST'])
def api_auth_use_env():
    """Login using credentials from .env file"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        return jsonify({
            'error': 'No credentials found in .env file. Please add LINKEDIN_EMAIL and LINKEDIN_PASSWORD.'
        }), 400

    # Call the login endpoint with env credentials
    return api_auth_login()


def background_search(search_params, search_id):
    """Background thread function to perform job search"""
    global current_search, scraper_instance

    scraper = None
    should_close_scraper = False

    try:
        # Update status
        with search_lock:
            current_search['message'] = 'Initializing search...'
            current_search['progress'] = 10

        # Use existing authenticated scraper or create new one
        with scraper_lock:
            if scraper_instance is not None and scraper_instance.is_logged_in:
                scraper = scraper_instance
                with search_lock:
                    current_search['message'] = 'Using authenticated session...'
            else:
                # Create new scraper instance
                scraper = LinkedInJobScraperAuth(headless=True, delay=2.0)
                should_close_scraper = True

        # Extract search parameters
        keywords = search_params['keywords']
        location = search_params.get('location', '')
        experience_level = search_params.get('experience', '')
        job_type = search_params.get('jobType', '')
        date_posted = search_params.get('datePosted', '')
        max_jobs = min(int(search_params.get('maxJobs', 25)), 100)  # Limit to 100
        get_details = search_params.get('getDetails', False)
        use_auth = search_params.get('useAuth', False)

        with search_lock:
            current_search['message'] = f'Searching for "{keywords}" jobs...'
            current_search['progress'] = 20

        # Build search URL
        search_url = scraper.build_search_url(
            keywords=keywords,
            location=location,
            experience_level=experience_level,
            job_type=job_type,
            date_posted=date_posted
        )

        # Perform authenticated search
        jobs = scraper.scrape_jobs_authenticated(
            search_url=search_url,
            max_jobs=max_jobs,
            require_login=use_auth  # Only require login if user requested it
        )

        # Clean the job data
        data_manager = JobDataManager()
        jobs = data_manager.clean_job_data(jobs)

        with search_lock:
            current_search['message'] = 'Processing results...'
            current_search['progress'] = 80

        # Update results
        with search_lock:
            current_search.update({
                'status': 'completed',
                'progress': 100,
                'jobs_found': len(jobs),
                'message': f'Found {len(jobs)} jobs',
                'jobs': jobs
            })

    except Exception as e:
        # Handle errors
        with search_lock:
            current_search.update({
                'status': 'error',
                'progress': 0,
                'message': f'Search failed: {str(e)}',
                'jobs': []
            })
    finally:
        # Close scraper if we created a temporary one
        if should_close_scraper and scraper is not None:
            try:
                scraper.close()
            except:
                pass


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Create job_data directory if it doesn't exist
    Path('job_data').mkdir(exist_ok=True)
    
    print("🚀 Starting LinkedIn Job Search Agent Web Interface")
    print("📱 Access the app at: http://localhost:8080")
    print("🎨 Material Design 3 interface ready!")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
