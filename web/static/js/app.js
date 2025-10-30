// LinkedIn Job Search Agent - Frontend Application

class JobSearchApp {
    constructor() {
        this.jobs = [];
        this.filteredJobs = [];
        this.searchInterval = null;
        this.isDarkTheme = false;
        this.isAuthenticated = false;
        this.hasEnvCredentials = false;

        // Pagination
        this.currentPage = 1;
        this.jobsPerPage = 20;

        // Sorting
        this.currentSort = 'relevance'; // relevance, date, company, title
        this.sortDirection = 'desc';

        // Filter debounce timer
        this.filterDebounceTimer = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTheme();
        this.setupScrollHandler();
        this.checkAuthStatus();
        this.checkExistingResults();
    }

    setupScrollHandler() {
        // Show/hide FAB on scroll
        window.addEventListener('scroll', () => {
            const fabContainer = document.getElementById('fab-container');
            if (fabContainer) {
                if (window.scrollY > 300) {
                    fabContainer.style.display = 'flex';
                } else {
                    fabContainer.style.display = 'none';
                }
            }
        });
    }
    
    setupEventListeners() {
        // Form submission
        const form = document.getElementById('job-search-form');
        form.addEventListener('submit', (e) => this.handleSearch(e));

        // Clear results
        const clearBtn = document.getElementById('clear-btn');
        clearBtn.addEventListener('click', () => this.clearResults());

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', () => this.toggleTheme());

        // Auth buttons
        const loginBtn = document.getElementById('login-btn');
        loginBtn.addEventListener('click', () => this.openLoginDialog());

        const logoutBtn = document.getElementById('logout-btn');
        logoutBtn.addEventListener('click', () => this.handleLogout());

        // Login dialog
        const loginDialog = document.getElementById('login-dialog');
        const loginSubmitBtn = document.getElementById('login-submit-btn');
        loginSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        const useEnvBtn = document.getElementById('use-env-btn');
        useEnvBtn.addEventListener('click', () => this.handleUseEnvCredentials());

        // Export buttons
        document.getElementById('export-csv').addEventListener('click', () => this.exportData('csv'));
        document.getElementById('export-json').addEventListener('click', () => this.exportData('json'));
        document.getElementById('export-excel').addEventListener('click', () => this.exportData('excel'));

        // Job filter
        const jobFilter = document.getElementById('job-filter');
        jobFilter.addEventListener('input', (e) => this.filterJobs(e.target.value));

        // Filter chips
        document.getElementById('filter-with-salary').addEventListener('click', (e) => {
            this.toggleFilterChip(e.target, 'salary');
        });

        document.getElementById('filter-remote').addEventListener('click', (e) => {
            this.toggleFilterChip(e.target, 'remote');
        });
    }
    
    setupTheme() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.isDarkTheme = savedTheme === 'dark';
        this.applyTheme();
    }
    
    toggleTheme() {
        this.isDarkTheme = !this.isDarkTheme;
        this.applyTheme();
        localStorage.setItem('theme', this.isDarkTheme ? 'dark' : 'light');
    }
    
    applyTheme() {
        const body = document.body;
        const themeIcon = document.querySelector('#theme-toggle md-icon');

        if (this.isDarkTheme) {
            body.setAttribute('data-theme', 'dark');
            themeIcon.textContent = 'light_mode';
        } else {
            body.removeAttribute('data-theme');
            themeIcon.textContent = 'dark_mode';
        }
    }

    // Authentication Methods
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();

            this.isAuthenticated = data.logged_in;
            this.hasEnvCredentials = data.has_env_credentials;

            this.updateAuthUI();
        } catch (error) {
            console.error('Failed to check auth status:', error);
        }
    }

    updateAuthUI() {
        const loginBtn = document.getElementById('login-btn');
        const authBadge = document.getElementById('auth-status-badge');
        const useAuthCheckbox = document.getElementById('use-auth');

        if (this.isAuthenticated) {
            loginBtn.style.display = 'none';
            authBadge.style.display = 'flex';
            if (useAuthCheckbox) useAuthCheckbox.checked = true;
        } else {
            loginBtn.style.display = 'block';
            authBadge.style.display = 'none';
        }
    }

    openLoginDialog() {
        const dialog = document.getElementById('login-dialog');
        const envNotice = document.getElementById('env-credentials-notice');
        const loginError = document.getElementById('login-error');

        // Show/hide env credentials notice
        if (this.hasEnvCredentials) {
            envNotice.style.display = 'flex';
        } else {
            envNotice.style.display = 'none';
        }

        // Hide any previous errors
        loginError.style.display = 'none';

        // Open dialog
        dialog.show();
    }

    async handleLogin() {
        const emailInput = document.getElementById('login-email');
        const passwordInput = document.getElementById('login-password');
        const loginError = document.getElementById('login-error');
        const loginErrorText = document.getElementById('login-error-text');
        const loginSubmitBtn = document.getElementById('login-submit-btn');

        const email = emailInput.value;
        const password = passwordInput.value;

        if (!email || !password) {
            loginErrorText.textContent = 'Please enter both email and password';
            loginError.style.display = 'flex';
            return;
        }

        // Show loading state
        loginSubmitBtn.disabled = true;
        loginSubmitBtn.textContent = 'Logging in...';
        loginError.style.display = 'none';

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                this.isAuthenticated = true;
                this.updateAuthUI();
                document.getElementById('login-dialog').close();
                this.showSnackbar('✅ Successfully logged in to LinkedIn!', 'success');

                // Clear form
                emailInput.value = '';
                passwordInput.value = '';
            } else {
                // Error
                loginErrorText.textContent = data.error || 'Login failed';
                loginError.style.display = 'flex';
            }
        } catch (error) {
            loginErrorText.textContent = 'Network error. Please try again.';
            loginError.style.display = 'flex';
        } finally {
            loginSubmitBtn.disabled = false;
            loginSubmitBtn.innerHTML = '<md-icon slot="icon">login</md-icon>Login';
        }
    }

    async handleUseEnvCredentials() {
        const useEnvBtn = document.getElementById('use-env-btn');
        const loginError = document.getElementById('login-error');
        const loginErrorText = document.getElementById('login-error-text');

        // Show loading state
        useEnvBtn.disabled = true;
        useEnvBtn.textContent = 'Logging in...';
        loginError.style.display = 'none';

        try {
            const response = await fetch('/api/auth/use-env', {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                this.isAuthenticated = true;
                this.updateAuthUI();
                document.getElementById('login-dialog').close();
                this.showSnackbar('✅ Successfully logged in using saved credentials!', 'success');
            } else {
                // Error
                loginErrorText.textContent = data.error || 'Login failed';
                loginError.style.display = 'flex';
            }
        } catch (error) {
            loginErrorText.textContent = 'Network error. Please try again.';
            loginError.style.display = 'flex';
        } finally {
            useEnvBtn.disabled = false;
            useEnvBtn.innerHTML = '<md-icon slot="icon">key</md-icon>Use Saved Credentials';
        }
    }

    async handleLogout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST'
            });

            if (response.ok) {
                this.isAuthenticated = false;
                this.updateAuthUI();
                this.showSnackbar('📤 Successfully logged out', 'info');
            }
        } catch (error) {
            this.showSnackbar('⚠️ Logout failed', 'error');
        }
    }

    async handleSearch(e) {
        e.preventDefault();

        // Check if auth is required but user is not logged in
        const useAuth = document.getElementById('use-auth')?.checked || false;
        if (useAuth && !this.isAuthenticated) {
            this.showSnackbar('⚠️ Please login first to use authentication', 'warning');
            this.openLoginDialog();
            return;
        }

        // Get form data
        const formData = new FormData(e.target);
        const searchParams = {
            keywords: document.getElementById('keywords').value,
            location: document.getElementById('location').value,
            experience: document.getElementById('experience').value,
            jobType: document.getElementById('job-type').value,
            datePosted: document.getElementById('date-posted').value,
            maxJobs: document.getElementById('max-jobs').value,
            getDetails: document.getElementById('get-details').checked,
            useAuth: useAuth
        };

        // Validate required fields
        if (!searchParams.keywords.trim()) {
            this.showSnackbar('Please enter job keywords', 'error');
            return;
        }
        
        try {
            // Start search
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchParams)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showProgressSection();
                this.hideResultsSection();
                this.startProgressPolling();
                this.showSnackbar('Job search started!', 'success');
            } else {
                this.showSnackbar(result.error || 'Failed to start search', 'error');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.showSnackbar('Failed to start search. Please try again.', 'error');
        }
    }
    
    async clearResults() {
        try {
            const response = await fetch('/api/clear');
            const result = await response.json();
            
            if (result.success) {
                this.hideProgressSection();
                this.hideResultsSection();
                this.jobs = [];
                this.filteredJobs = [];
                this.showSnackbar('Results cleared', 'success');
            } else {
                this.showSnackbar(result.error || 'Failed to clear results', 'error');
            }
        } catch (error) {
            console.error('Clear error:', error);
            this.showSnackbar('Failed to clear results', 'error');
        }
    }
    
    startProgressPolling() {
        if (this.searchInterval) {
            clearInterval(this.searchInterval);
        }
        
        this.searchInterval = setInterval(() => {
            this.checkSearchStatus();
        }, 2000); // Poll every 2 seconds
    }
    
    async checkSearchStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.updateProgress(status);
            
            if (status.status === 'completed') {
                clearInterval(this.searchInterval);
                this.searchInterval = null;
                await this.loadResults();
                this.hideProgressSection();
                this.showResultsSection();
                this.showSnackbar(`Found ${status.jobs_found} jobs!`, 'success');
            } else if (status.status === 'error') {
                clearInterval(this.searchInterval);
                this.searchInterval = null;
                this.hideProgressSection();
                this.showSnackbar(status.message || 'Search failed', 'error');
            }
            
        } catch (error) {
            console.error('Status check error:', error);
            clearInterval(this.searchInterval);
            this.searchInterval = null;
            this.hideProgressSection();
            this.showSnackbar('Connection error', 'error');
        }
    }
    
    updateProgress(status) {
        const progressTitle = document.getElementById('progress-title');
        const progressMessage = document.getElementById('progress-message');
        
        if (status.status === 'searching') {
            progressTitle.textContent = 'Searching...';
            progressMessage.textContent = status.message || 'Searching for jobs...';
        }
    }
    
    async loadResults() {
        try {
            const response = await fetch('/api/results');
            const data = await response.json();

            this.jobs = data.jobs || [];
            this.filteredJobs = [...this.jobs];
            this.currentPage = 1; // Reset pagination

            this.renderJobCards();
            this.updateResultsHeader();
            this.renderStatistics(); // Render statistics dashboard

        } catch (error) {
            console.error('Load results error:', error);
            this.showSnackbar('Failed to load results', 'error');
        }
    }
    
    async checkExistingResults() {
        try {
            const response = await fetch('/api/results');
            const data = await response.json();

            if (data.jobs && data.jobs.length > 0) {
                this.jobs = data.jobs;
                this.filteredJobs = [...this.jobs];
                this.currentPage = 1;
                this.showResultsSection();
                this.renderJobCards();
                this.updateResultsHeader();
                this.renderStatistics(); // Render statistics
            }

        } catch (error) {
            // Ignore errors on initial load
            console.log('No existing results');
        }
    }
    
    renderJobCards() {
        const container = document.getElementById('job-cards-container');

        if (this.filteredJobs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="material-symbols-outlined">work_off</span>
                    <h3 class="md-typescale-headline-small">No jobs found</h3>
                    <p class="md-typescale-body-medium">Try adjusting your search criteria</p>
                </div>
            `;
            return;
        }

        // Get paginated jobs
        const paginatedJobs = this.getPaginatedJobs();
        container.innerHTML = paginatedJobs.map(job => this.createJobCard(job)).join('');

        // Render pagination controls
        this.renderPagination();
    }
    
    createJobCard(job) {
        const location = job.location || 'Not specified';
        const postedDate = job.posted_date || 'Recently';
        const description = job.description_snippet || job.full_description || 'No description available';

        // Truncate description
        const truncatedDescription = description.length > 200
            ? description.substring(0, 200) + '...'
            : description;

        // Create badges for new jobs
        const badges = [];
        if (this.isJobNew(job)) {
            badges.push(`<span class="badge new"><span class="material-symbols-outlined">new_releases</span>New</span>`);
        }
        if (job.salary && job.salary.trim()) {
            // Featured if it has salary info
            badges.push(`<span class="badge featured"><span class="material-symbols-outlined">star</span>Featured</span>`);
        }

        const badgesHtml = badges.length > 0
            ? `<div class="job-card-badge">${badges.join('')}</div>`
            : '';

        // Create tags based on available data
        const tags = [];
        if (job.employment_type) tags.push(job.employment_type);
        if (job.seniority_level) tags.push(job.seniority_level);
        if (job.industry) tags.push(job.industry);

        const tagsHtml = tags.slice(0, 3).map(tag =>
            `<span class="job-tag">${this.escapeHtml(tag)}</span>`
        ).join('');

        // Enhanced salary display with icon
        const salaryHtml = job.salary
            ? `<span class="job-salary"><span class="material-symbols-outlined">payments</span>${this.escapeHtml(job.salary)}</span>`
            : '';

        return `
            <div class="job-card" data-job-id="${job.job_id}">
                ${badgesHtml}

                <div class="job-card-header">
                    <div class="job-info">
                        <h3 class="job-title md-typescale-title-medium">
                            <span class="material-symbols-outlined">work</span>
                            <a href="${job.job_url}" target="_blank" rel="noopener">
                                ${this.escapeHtml(job.title)}
                            </a>
                        </h3>
                        <h4 class="job-company md-typescale-title-small">
                            <span class="material-symbols-outlined">domain</span>
                            <a href="${job.company_url}" target="_blank" rel="noopener">
                                ${this.escapeHtml(job.company)}
                            </a>
                        </h4>
                    </div>
                    ${salaryHtml}
                </div>

                <div class="job-meta">
                    <div class="job-meta-item">
                        <span class="material-symbols-outlined">location_on</span>
                        <span>${this.escapeHtml(location)}</span>
                    </div>
                    <div class="job-meta-item">
                        <span class="material-symbols-outlined">schedule</span>
                        <span>${this.escapeHtml(postedDate)}</span>
                    </div>
                </div>

                <p class="job-description md-typescale-body-medium">
                    ${this.escapeHtml(truncatedDescription)}
                </p>

                <div class="job-actions">
                    <div class="job-tags">
                        ${tagsHtml}
                    </div>
                    <div class="job-buttons">
                        <md-text-button onclick="window.open('${job.job_url}', '_blank')">
                            <md-icon slot="icon">open_in_new</md-icon>
                            View Job
                        </md-text-button>
                    </div>
                </div>
            </div>
        `;
    }
    
    filterJobs(searchTerm) {
        // Debounce the filter to avoid excessive re-renders
        clearTimeout(this.filterDebounceTimer);

        this.filterDebounceTimer = setTimeout(() => {
            const term = searchTerm.toLowerCase();

            this.filteredJobs = this.jobs.filter(job => {
                return (
                    job.title.toLowerCase().includes(term) ||
                    job.company.toLowerCase().includes(term) ||
                    job.location.toLowerCase().includes(term) ||
                    (job.description_snippet && job.description_snippet.toLowerCase().includes(term))
                );
            });

            this.currentPage = 1; // Reset to first page
            this.renderJobCards();
            this.updateResultsHeader();
        }, 300); // Wait 300ms after user stops typing
    }
    
    toggleFilterChip(chip, filterType) {
        const isActive = chip.hasAttribute('selected');
        
        if (isActive) {
            chip.removeAttribute('selected');
        } else {
            chip.setAttribute('selected', '');
        }
        
        this.applyFilters();
    }
    
    applyFilters() {
        const withSalaryFilter = document.getElementById('filter-with-salary').hasAttribute('selected');
        const remoteFilter = document.getElementById('filter-remote').hasAttribute('selected');
        const searchTerm = document.getElementById('job-filter').value.toLowerCase();
        
        this.filteredJobs = this.jobs.filter(job => {
            // Text search filter
            let matchesSearch = true;
            if (searchTerm) {
                matchesSearch = (
                    job.title.toLowerCase().includes(searchTerm) ||
                    job.company.toLowerCase().includes(searchTerm) ||
                    job.location.toLowerCase().includes(searchTerm) ||
                    (job.description_snippet && job.description_snippet.toLowerCase().includes(searchTerm))
                );
            }
            
            // Salary filter
            let matchesSalary = true;
            if (withSalaryFilter) {
                matchesSalary = job.salary && job.salary.trim() !== '';
            }
            
            // Remote filter
            let matchesRemote = true;
            if (remoteFilter) {
                matchesRemote = job.location.toLowerCase().includes('remote');
            }
            
            return matchesSearch && matchesSalary && matchesRemote;
        });
        
        this.renderJobCards();
        this.updateResultsHeader();
    }
    
    updateResultsHeader() {
        const resultsTitle = document.getElementById('results-title');
        const resultsSummary = document.getElementById('results-summary');
        
        const total = this.jobs.length;
        const filtered = this.filteredJobs.length;
        
        resultsTitle.textContent = `Job Results (${filtered})`;
        
        if (filtered === total) {
            resultsSummary.textContent = `Showing all ${total} jobs`;
        } else {
            resultsSummary.textContent = `Showing ${filtered} of ${total} jobs`;
        }
    }
    
    async exportData(format) {
        if (this.jobs.length === 0) {
            this.showSnackbar('No jobs to export', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/export/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `linkedin_jobs_export.${format === 'excel' ? 'xlsx' : format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSnackbar(`Exported ${this.jobs.length} jobs to ${format.toUpperCase()}`, 'success');
            } else {
                const error = await response.json();
                this.showSnackbar(error.error || 'Export failed', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showSnackbar('Export failed', 'error');
        }
    }
    
    showProgressSection() {
        document.getElementById('progress-section').style.display = 'block';
    }
    
    hideProgressSection() {
        document.getElementById('progress-section').style.display = 'none';
    }
    
    showResultsSection() {
        document.getElementById('results-section').style.display = 'block';
    }
    
    hideResultsSection() {
        document.getElementById('results-section').style.display = 'none';
    }
    
    showSnackbar(message, type = 'info') {
        // Remove existing snackbars
        const existingSnackbars = document.querySelectorAll('.snackbar');
        existingSnackbars.forEach(snackbar => snackbar.remove());
        
        // Create new snackbar
        const snackbar = document.createElement('div');
        snackbar.className = `snackbar ${type}`;
        
        const icon = this.getSnackbarIcon(type);
        
        snackbar.innerHTML = `
            <span class="material-symbols-outlined">${icon}</span>
            <span>${this.escapeHtml(message)}</span>
        `;
        
        // Add to page
        document.body.appendChild(snackbar);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (snackbar.parentNode) {
                snackbar.remove();
            }
        }, 5000);
        
        // Remove on click
        snackbar.addEventListener('click', () => {
            snackbar.remove();
        });
    }
    
    getSnackbarIcon(type) {
        switch (type) {
            case 'success': return 'check_circle';
            case 'error': return 'error';
            case 'warning': return 'warning';
            default: return 'info';
        }
    }
    
    escapeHtml(text) {
        if (typeof text !== 'string') return '';

        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================
    // ENHANCED FEATURES
    // ============================================

    sortJobs(sortBy) {
        this.currentSort = sortBy;

        this.filteredJobs.sort((a, b) => {
            let compareA, compareB;

            switch (sortBy) {
                case 'title':
                    compareA = a.title.toLowerCase();
                    compareB = b.title.toLowerCase();
                    break;
                case 'company':
                    compareA = a.company.toLowerCase();
                    compareB = b.company.toLowerCase();
                    break;
                case 'date':
                    // Parse date if available, otherwise use scraped_at
                    compareA = a.posted_date || a.scraped_at || '';
                    compareB = b.posted_date || b.scraped_at || '';
                    break;
                case 'location':
                    compareA = a.location.toLowerCase();
                    compareB = b.location.toLowerCase();
                    break;
                default: // relevance
                    return 0;
            }

            if (compareA < compareB) return this.sortDirection === 'asc' ? -1 : 1;
            if (compareA > compareB) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.currentPage = 1; // Reset to first page
        this.renderJobCards();
        this.updateSortUI();
    }

    toggleSortDirection() {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        this.sortJobs(this.currentSort);
    }

    updateSortUI() {
        // Update active sort button if sort UI exists
        document.querySelectorAll('.sort-button').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.sort === this.currentSort) {
                btn.classList.add('active');
            }
        });
    }

    getPaginatedJobs() {
        const startIndex = (this.currentPage - 1) * this.jobsPerPage;
        const endIndex = startIndex + this.jobsPerPage;
        return this.filteredJobs.slice(startIndex, endIndex);
    }

    getTotalPages() {
        return Math.ceil(this.filteredJobs.length / this.jobsPerPage);
    }

    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page < 1 || page > totalPages) return;

        this.currentPage = page;
        this.renderJobCards();
        this.renderPagination();

        // Scroll to top of results
        document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
    }

    renderPagination() {
        const paginationContainer = document.getElementById('pagination-container');
        if (!paginationContainer) return;

        const totalPages = this.getTotalPages();
        if (totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }

        paginationContainer.style.display = 'flex';

        let html = `
            <button class="pagination-button" ${this.currentPage === 1 ? 'disabled' : ''} onclick="window.jobSearchApp.goToPage(${this.currentPage - 1})">
                <span class="material-symbols-outlined">chevron_left</span>
            </button>
        `;

        // Show page numbers (max 5 visible)
        const maxVisible = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);

        if (endPage - startPage + 1 < maxVisible) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        if (startPage > 1) {
            html += `<button class="pagination-button" onclick="window.jobSearchApp.goToPage(1)">1</button>`;
            if (startPage > 2) {
                html += `<span class="pagination-info">...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<button class="pagination-button ${i === this.currentPage ? 'active' : ''}" onclick="window.jobSearchApp.goToPage(${i})">${i}</button>`;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<span class="pagination-info">...</span>`;
            }
            html += `<button class="pagination-button" onclick="window.jobSearchApp.goToPage(${totalPages})">${totalPages}</button>`;
        }

        html += `
            <button class="pagination-button" ${this.currentPage === totalPages ? 'disabled' : ''} onclick="window.jobSearchApp.goToPage(${this.currentPage + 1})">
                <span class="material-symbols-outlined">chevron_right</span>
            </button>
            <span class="pagination-info">Page ${this.currentPage} of ${totalPages}</span>
        `;

        paginationContainer.innerHTML = html;
    }

    calculateStatistics() {
        if (this.jobs.length === 0) return null;

        // Count jobs by company
        const companyCounts = {};
        const locationCounts = {};
        let salaryCount = 0;
        let remoteCount = 0;

        this.jobs.forEach(job => {
            // Company stats
            const company = job.company || 'Unknown';
            companyCounts[company] = (companyCounts[company] || 0) + 1;

            // Location stats
            const location = job.location || 'Not specified';
            locationCounts[location] = (locationCounts[location] || 0) + 1;

            // Salary stats
            if (job.salary && job.salary.trim()) {
                salaryCount++;
            }

            // Remote stats
            if (location.toLowerCase().includes('remote')) {
                remoteCount++;
            }
        });

        // Get top companies
        const topCompanies = Object.entries(companyCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([company, count]) => ({ company, count }));

        // Get top locations
        const topLocations = Object.entries(locationCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([location, count]) => ({ location, count }));

        return {
            totalJobs: this.jobs.length,
            withSalary: salaryCount,
            remoteJobs: remoteCount,
            topCompanies,
            topLocations,
            uniqueCompanies: Object.keys(companyCounts).length,
            uniqueLocations: Object.keys(locationCounts).length
        };
    }

    renderStatistics() {
        const statsContainer = document.getElementById('stats-container');
        if (!statsContainer) return;

        const stats = this.calculateStatistics();
        if (!stats) {
            statsContainer.style.display = 'none';
            return;
        }

        statsContainer.style.display = 'block';

        const html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="material-symbols-outlined stat-icon">work</span>
                    <div class="stat-value">${stats.totalJobs}</div>
                    <div class="stat-label">Total Jobs</div>
                </div>
                <div class="stat-card">
                    <span class="material-symbols-outlined stat-icon">domain</span>
                    <div class="stat-value">${stats.uniqueCompanies}</div>
                    <div class="stat-label">Companies</div>
                </div>
                <div class="stat-card">
                    <span class="material-symbols-outlined stat-icon">location_on</span>
                    <div class="stat-value">${stats.uniqueLocations}</div>
                    <div class="stat-label">Locations</div>
                </div>
                <div class="stat-card">
                    <span class="material-symbols-outlined stat-icon">attach_money</span>
                    <div class="stat-value">${stats.withSalary}</div>
                    <div class="stat-label">With Salary</div>
                </div>
                <div class="stat-card">
                    <span class="material-symbols-outlined stat-icon">home_work</span>
                    <div class="stat-value">${stats.remoteJobs}</div>
                    <div class="stat-label">Remote Jobs</div>
                </div>
            </div>
        `;

        statsContainer.innerHTML = html;
    }

    showLoadingSkeleton() {
        const container = document.getElementById('job-cards-container');
        if (!container) return;

        const skeletonHtml = Array(5).fill(0).map(() => `
            <div class="skeleton-card">
                <div class="skeleton-line title"></div>
                <div class="skeleton-line subtitle"></div>
                <div style="display: flex; gap: 16px; margin: 20px 0;">
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line short"></div>
                </div>
                <div class="skeleton-line long"></div>
                <div class="skeleton-line medium"></div>
                <div class="skeleton-line short"></div>
            </div>
        `).join('');

        container.innerHTML = `<div class="skeleton-container">${skeletonHtml}</div>`;
    }

    isJobNew(job) {
        // Check if job was posted in the last 24 hours
        const postedDate = job.posted_date || '';
        return postedDate.toLowerCase().includes('hour') ||
               postedDate.toLowerCase().includes('minute') ||
               postedDate.toLowerCase().includes('today');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jobSearchApp = new JobSearchApp();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', (event) => {
    if (window.jobSearchApp) {
        window.jobSearchApp.checkExistingResults();
    }
});