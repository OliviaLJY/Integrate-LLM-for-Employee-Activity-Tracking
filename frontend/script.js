// Configuration
const API_BASE_URL = 'http://localhost:8000';
let queryCount = 0;

// DOM Elements
const queryInput = document.getElementById('queryInput');
const queryBtn = document.getElementById('queryBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const clearResultsBtn = document.getElementById('clearResults');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');
const totalQueriesSpan = document.getElementById('totalQueries');

// Example query buttons
const exampleBtns = document.querySelectorAll('.example-btn');
const actionCards = document.querySelectorAll('.action-card');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadEmployeeCount();
});

// Event Listeners
function initializeEventListeners() {
    // Query input and button
    queryBtn.addEventListener('click', handleQuery);
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleQuery();
        }
    });

    // Example query buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            queryInput.value = query;
            handleQuery();
        });
    });

    // Clear results button
    clearResultsBtn.addEventListener('click', clearResults);

    // Action cards
    document.getElementById('viewEmployees').addEventListener('click', viewAllEmployees);
    document.getElementById('runBenchmark').addEventListener('click', runBenchmark);
    document.getElementById('viewActivities').addEventListener('click', viewRecentActivities);
    document.getElementById('exportData').addEventListener('click', exportData);
}

// Main query handler
async function handleQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showToast('Please enter a question', 'warning');
        return;
    }

    showLoading(true);
    disableQueryButton(true);

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResult(data);
        updateQueryCount();
        showToast('Query executed successfully!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to execute query. Please check if the server is running.', 'error');
    } finally {
        showLoading(false);
        disableQueryButton(false);
    }
}

// Display query result
function displayResult(data) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    const executionTime = (data.execution_time || 0).toFixed(3);
    const hasError = data.error !== null;
    
    resultItem.innerHTML = `
        <div class="result-query">
            <i class="fas fa-question-circle"></i>
            ${escapeHtml(data.query)}
        </div>
        <div class="result-response ${hasError ? 'error' : ''}">
            ${hasError ? `<strong>Error:</strong> ${escapeHtml(data.error)}` : escapeHtml(data.response)}
        </div>
        <div class="result-meta">
            <div class="result-time">
                <i class="fas fa-clock"></i>
                Executed in ${executionTime}s
            </div>
            <div class="result-confidence">
                <i class="fas fa-chart-line"></i>
                Confidence: ${((data.confidence || 0) * 100).toFixed(0)}%
            </div>
        </div>
        ${data.sql_query ? `<div class="result-sql">${escapeHtml(data.sql_query)}</div>` : ''}
    `;

    resultsContent.insertBefore(resultItem, resultsContent.firstChild);
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load employee count
async function loadEmployeeCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/employees/`);
        if (response.ok) {
            const employees = await response.json();
            document.getElementById('totalEmployees').textContent = employees.length;
        }
    } catch (error) {
        console.error('Error loading employee count:', error);
    }
}

// View all employees
async function viewAllEmployees() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/employees/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const employees = await response.json();
        displayEmployeesList(employees);
        showToast('Employee list loaded successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load employees', 'error');
    } finally {
        showLoading(false);
    }
}

// Display employees list
function displayEmployeesList(employees) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    let employeesList = employees.map(emp => 
        `<div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 6px;">
            <strong>${escapeHtml(emp.full_name)}</strong> - ${escapeHtml(emp.job_title)}<br>
            <small>${escapeHtml(emp.email)} | ${escapeHtml(emp.department)} | Hired: ${emp.hire_date}</small>
        </div>`
    ).join('');
    
    resultItem.innerHTML = `
        <div class="result-query">
            <i class="fas fa-users"></i>
            All Employees (${employees.length} total)
        </div>
        <div class="result-response">
            ${employeesList}
        </div>
        <div class="result-meta">
            <div class="result-time">
                <i class="fas fa-info-circle"></i>
                System query
            </div>
        </div>
    `;

    resultsContent.insertBefore(resultItem, resultsContent.firstChild);
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Run benchmark
async function runBenchmark() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/benchmark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayBenchmarkResults(data);
        showToast('Benchmark completed successfully!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to run benchmark', 'error');
    } finally {
        showLoading(false);
    }
}

// Display benchmark results
function displayBenchmarkResults(data) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    const successRate = ((data.successful_queries / data.total_queries) * 100).toFixed(1);
    const avgTime = data.average_execution_time.toFixed(3);
    
    let queryTypesList = Object.entries(data.query_type_distribution)
        .map(([type, count]) => `<span style="margin-right: 15px;"><strong>${type}:</strong> ${count}</span>`)
        .join('');
    
    resultItem.innerHTML = `
        <div class="result-query">
            <i class="fas fa-chart-bar"></i>
            Benchmark Results - 20 Test Queries
        </div>
        <div class="result-response">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: #f0fff4; padding: 15px; border-radius: 8px; border-left: 4px solid #48bb78;">
                    <div style="font-size: 2rem; font-weight: bold; color: #38a169;">${data.successful_queries}/${data.total_queries}</div>
                    <div style="color: #4a5568;">Success Rate: ${successRate}%</div>
                </div>
                <div style="background: #f7fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${avgTime}s</div>
                    <div style="color: #4a5568;">Avg Execution Time</div>
                </div>
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Query Types:</strong><br>
                ${queryTypesList}
            </div>
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; font-weight: 600; margin-bottom: 10px;">View Individual Results</summary>
                <div style="max-height: 300px; overflow-y: auto;">
                    ${data.results.slice(0, 5).map((result, index) => `
                        <div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 6px; border-left: 3px solid ${result.success ? '#48bb78' : '#e53e3e'};">
                            <div style="font-weight: 600; margin-bottom: 5px;">${index + 1}. ${escapeHtml(result.query)}</div>
                            <div style="color: #4a5568; margin-bottom: 5px;">${escapeHtml(result.response)}</div>
                            <div style="font-size: 0.8rem; color: #718096;">Time: ${result.execution_time.toFixed(3)}s</div>
                        </div>
                    `).join('')}
                    ${data.results.length > 5 ? `<div style="text-align: center; color: #718096; font-style: italic;">... and ${data.results.length - 5} more results</div>` : ''}
                </div>
            </details>
        </div>
        <div class="result-meta">
            <div class="result-time">
                <i class="fas fa-stopwatch"></i>
                Benchmark completed
            </div>
        </div>
    `;

    resultsContent.insertBefore(resultItem, resultsContent.firstChild);
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// View recent activities
async function viewRecentActivities() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/activities/?limit=10`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const activities = await response.json();
        displayActivitiesList(activities);
        showToast('Recent activities loaded!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load activities', 'error');
    } finally {
        showLoading(false);
    }
}

// Display activities list
function displayActivitiesList(activities) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    let activitiesList = activities.slice(0, 10).map(activity => 
        `<div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 6px;">
            <div style="font-weight: 600;">Week ${activity.week_number} - Employee ID: ${activity.employee_id}</div>
            <div style="margin: 5px 0; color: #4a5568;">
                Hours: ${activity.hours_worked} | Sales: ¥${activity.total_sales || 'N/A'} | Meetings: ${activity.meetings_attended}
            </div>
            <div style="font-size: 0.9rem; color: #718096;">${escapeHtml(activity.activities || 'No activities recorded')}</div>
        </div>`
    ).join('');
    
    resultItem.innerHTML = `
        <div class="result-query">
            <i class="fas fa-tasks"></i>
            Recent Activities (Last 10 records)
        </div>
        <div class="result-response">
            ${activitiesList}
        </div>
        <div class="result-meta">
            <div class="result-time">
                <i class="fas fa-info-circle"></i>
                System query
            </div>
        </div>
    `;

    resultsContent.insertBefore(resultItem, resultsContent.firstChild);
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Export data functionality
function exportData() {
    const modal = document.createElement('div');
    modal.className = 'export-modal';
    modal.innerHTML = `
        <div class="export-modal-content">
            <div class="export-modal-header">
                <h3>Export Data</h3>
                <button class="close-modal" onclick="closeExportModal()">&times;</button>
            </div>
            <div class="export-modal-body">
                <p>Choose what to export and in which format:</p>
                
                <div class="export-options">
                    <div class="export-section">
                        <h4>📊 Employee Data</h4>
                        <p>Export all employee information including names, departments, and job titles</p>
                        <div class="export-buttons">
                            <button onclick="downloadExport('employees', 'csv')" class="export-btn csv-btn">
                                📄 CSV Format
                            </button>
                            <button onclick="downloadExport('employees', 'json')" class="export-btn json-btn">
                                📋 JSON Format
                            </button>
                        </div>
                    </div>
                    
                    <div class="export-section">
                        <h4>📈 Activity Data</h4>
                        <p>Export all employee activities including hours, sales, and meetings</p>
                        <div class="export-buttons">
                            <button onclick="downloadExport('activities', 'csv')" class="export-btn csv-btn">
                                📄 CSV Format
                            </button>
                            <button onclick="downloadExport('activities', 'json')" class="export-btn json-btn">
                                📋 JSON Format
                            </button>
                        </div>
                    </div>
                    
                    <div class="export-section">
                        <h4>📋 Summary Report</h4>
                        <p>Export summary statistics and department analytics</p>
                        <div class="export-buttons">
                            <button onclick="downloadExport('summary', 'csv')" class="export-btn csv-btn">
                                📄 CSV Format
                            </button>
                            <button onclick="downloadExport('summary', 'json')" class="export-btn json-btn">
                                📋 JSON Format
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listener to close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeExportModal();
        }
    });
}

function closeExportModal() {
    const modal = document.querySelector('.export-modal');
    if (modal) {
        modal.remove();
    }
}

async function downloadExport(dataType, format) {
    try {
        showToast(`Preparing ${dataType} export in ${format.toUpperCase()} format...`, 'info');
        
        const response = await fetch(`${API_BASE_URL}/export/${dataType}/${format}`);
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }
        
        // Get the filename from the Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `${dataType}_export.${format}`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename=(.+)/);
            if (filenameMatch) {
                filename = filenameMatch[1].replace(/"/g, '');
            }
        }
        
        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast(`${dataType} data exported successfully as ${filename}`, 'success');
        closeExportModal();
        
    } catch (error) {
        console.error('Export error:', error);
        showToast(`Export failed: ${error.message}`, 'error');
    }
}

// Utility functions
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function disableQueryButton(disable) {
    queryBtn.disabled = disable;
    if (disable) {
        queryBtn.innerHTML = '<span class="btn-text">Processing...</span><i class="fas fa-spinner fa-spin"></i>';
    } else {
        queryBtn.innerHTML = '<span class="btn-text">Ask</span><i class="fas fa-paper-plane"></i>';
    }
}

function clearResults() {
    resultsContent.innerHTML = '';
    resultsSection.style.display = 'none';
    queryCount = 0;
    updateQueryCount();
    showToast('Results cleared', 'success');
}

function updateQueryCount() {
    queryCount++;
    totalQueriesSpan.textContent = queryCount;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 'exclamation-triangle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 4000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle connection errors gracefully
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    if (event.reason.message && event.reason.message.includes('fetch')) {
        showToast('Connection error. Please ensure the server is running on http://localhost:8000', 'error');
    }
}); 