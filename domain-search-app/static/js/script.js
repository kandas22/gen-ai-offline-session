/**
 * Domain Search Application - Frontend JavaScript
 */

// DOM Elements
const searchForm = document.getElementById('searchForm');
const domainInput = document.getElementById('domainInput');
const searchButton = document.getElementById('searchButton');
const resultsContainer = document.getElementById('resultsContainer');
const errorContainer = document.getElementById('errorContainer');

// Event Listeners
searchForm.addEventListener('submit', handleSearch);

/**
 * Handle search form submission
 */
async function handleSearch(event) {
    event.preventDefault();
    
    const domain = domainInput.value.trim();
    
    if (!domain) {
        showError('Please enter a domain name');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    hideResults();
    hideError();
    
    try {
        // Make API request
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain })
        });
        
        const data = await response.json();
        
        // Handle response
        if (data.success) {
            displayResults(data.data);
        } else {
            showError(data.message || 'Domain information not found');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError('Network error occurred. Please check your connection and try again.');
    } finally {
        setLoadingState(false);
    }
}

/**
 * Set loading state for search button
 */
function setLoadingState(isLoading) {
    if (isLoading) {
        searchButton.classList.add('loading');
        searchButton.disabled = true;
        domainInput.disabled = true;
    } else {
        searchButton.classList.remove('loading');
        searchButton.disabled = false;
        domainInput.disabled = false;
    }
}

/**
 * Display search results
 */
function displayResults(data) {
    hideError();
    
    const html = `
        <div class="result-header">
            <h2>${data.domain_name || 'Domain Information'}</h2>
        </div>
        
        <div class="result-section">
            <h3>Domain Details</h3>
            <div class="result-grid">
                <div class="result-item">
                    <div class="result-label">Domain Name</div>
                    <div class="result-value">${formatValue(data.domain_name)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Registrar</div>
                    <div class="result-value">${formatValue(data.registrar)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Created Date</div>
                    <div class="result-value">${formatDate(data.created_date)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Updated Date</div>
                    <div class="result-value">${formatDate(data.updated_date)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Expires Date</div>
                    <div class="result-value">${formatDate(data.expires_date)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Status</div>
                    <div class="result-value">${formatValue(data.status)}</div>
                </div>
            </div>
        </div>
        
        ${data.registrant ? `
            <div class="result-section">
                <h3>Registrant Information</h3>
                <div class="result-grid">
                    <div class="result-item">
                        <div class="result-label">Name</div>
                        <div class="result-value">${formatValue(data.registrant.name)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Organization</div>
                        <div class="result-value">${formatValue(data.registrant.organization)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Country</div>
                        <div class="result-value">${formatValue(data.registrant.country)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Email</div>
                        <div class="result-value">${formatValue(data.registrant.email)}</div>
                    </div>
                </div>
            </div>
        ` : ''}
        
        ${data.name_servers && data.name_servers.length > 0 ? `
            <div class="result-section">
                <h3>Name Servers</h3>
                <ul class="name-servers-list">
                    ${data.name_servers.map(ns => `<li>${formatValue(ns)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
    `;
    
    resultsContainer.innerHTML = html;
    resultsContainer.classList.remove('hidden');
    
    // Smooth scroll to results
    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Show error message
 */
function showError(message) {
    hideResults();
    
    const html = `
        <div class="error-icon">⚠️</div>
        <div class="error-message">${message}</div>
        <div class="error-details">Please try again or check your API configuration.</div>
    `;
    
    errorContainer.innerHTML = html;
    errorContainer.classList.remove('hidden');
    
    // Smooth scroll to error
    setTimeout(() => {
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Hide results container
 */
function hideResults() {
    resultsContainer.classList.add('hidden');
}

/**
 * Hide error container
 */
function hideError() {
    errorContainer.classList.add('hidden');
}

/**
 * Format value for display
 */
function formatValue(value) {
    if (!value || value === 'N/A' || value === null || value === undefined) {
        return '<span style="color: var(--text-muted);">Not available</span>';
    }
    
    // Handle arrays
    if (Array.isArray(value)) {
        return value.join(', ') || '<span style="color: var(--text-muted);">Not available</span>';
    }
    
    // Handle objects
    if (typeof value === 'object') {
        return JSON.stringify(value);
    }
    
    return value;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString || dateString === 'N/A') {
        return '<span style="color: var(--text-muted);">Not available</span>';
    }
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return dateString;
        }
        
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

// Add input validation
domainInput.addEventListener('input', function(e) {
    // Remove invalid characters
    this.value = this.value.replace(/[^a-zA-Z0-9.-]/g, '');
});

// Add keyboard shortcut (Ctrl/Cmd + Enter to search)
domainInput.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        searchForm.dispatchEvent(new Event('submit'));
    }
});
