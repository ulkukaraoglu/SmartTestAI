// API base URL — same origin as the backend
const API_BASE_URL = window.location.origin;

// Global state
let uploadedFiles = [];
let scanResults = {};

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const fileList = document.getElementById('fileList');
const fileListItems = document.getElementById('fileListItems');
const scanButton = document.getElementById('scanButton');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('resultsContainer');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');

// Event listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
scanButton.addEventListener('click', startScan);

// Drag and drop
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function handleFiles(files) {
    uploadedFiles = files;
    displayFileList();
    scanButton.disabled = false;
}

function displayFileList() {
    if (uploadedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }

    fileList.style.display = 'block';
    fileListItems.innerHTML = '';

    uploadedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
        `;
        fileListItems.appendChild(li);
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Scan flow
async function startScan() {
    if (uploadedFiles.length === 0) {
        alert('Please upload at least one file first.');
        return;
    }

    scanButton.disabled = true;
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsContainer.style.display = 'none';
    errorState.style.display = 'none';

    try {
        updateScanStep(1, 'active');
        const projectName = await uploadFiles();
        updateScanStep(1, 'completed');
        
        updateScanStep(2, 'active');
        const snykResult = await runSnykScan(projectName);
        updateScanStep(2, 'completed');
        
        updateScanStep(3, 'active');
        const deepsourceResult = await runDeepSourceScan(projectName);
        updateScanStep(3, 'completed');
        
        updateScanStep(4, 'active');
        scanResults = {
            snyk: snykResult,
            deepsource: deepsourceResult
        };
        updateScanStep(4, 'completed');
        
        displayResults();
        
    } catch (error) {
        console.error('Scan error:', error);
        showError(error.message || 'An error occurred during the scan.');
    }
}

async function uploadFiles() {
    const formData = new FormData();
    uploadedFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();
        return result.project_name;
    } catch (error) {
        throw new Error(`Could not upload files: ${error.message}`);
    }
}

async function runSnykScan(projectName) {
    try {
        const response = await fetch(`${API_BASE_URL}/scan/code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project: projectName })
        });

        const result = await response.json();

        if (!response.ok) {
            const errorMsg = result.error || result.message || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(`Snyk scan error: ${errorMsg}`);
        }
        
        if (!result.success) {
            const errorMsg = result.error || 'Snyk scan failed';
            throw new Error(errorMsg);
        }

        return result;
    } catch (error) {
        console.error('Snyk scan error:', error);
        return {
            success: false,
            error: error.message,
            metrics: {
                tool_name: 'Snyk Code',
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
                total_issues: 0,
                scan_duration: 0
            },
            advanced_metrics: {}
        };
    }
}

async function runDeepSourceScan(projectName) {
    try {
        const response = await fetch(`${API_BASE_URL}/scan/deepsource`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project: projectName })
        });

        const result = await response.json();

        if (!response.ok) {
            const errorMsg = result.error || result.message || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(`DeepSource scan error: ${errorMsg}`);
        }
        
        if (!result.success) {
            const errorMsg = result.error || 'DeepSource scan failed';
            throw new Error(errorMsg);
        }

        return result;
    } catch (error) {
        console.error('DeepSource scan error:', error);
        return {
            success: false,
            error: error.message,
            metrics: {
                tool_name: 'DeepSource',
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
                total_issues: 0,
                scan_duration: 0
            },
            advanced_metrics: {}
        };
    }
}

function updateScanStep(stepNumber, status) {
    const step = document.getElementById(`step${stepNumber}`);
    if (step) {
        step.className = `scan-step ${status}`;
        const icon = step.querySelector('.step-icon');
        if (status === 'completed') {
            icon.textContent = '✓';
        }
    }
}

function displayResults() {
    loadingState.style.display = 'none';
    resultsContainer.style.display = 'block';

    if (scanResults.snyk && scanResults.snyk.success) {
        displaySnykResults(scanResults.snyk);
    } else {
        displayError('snyk', scanResults.snyk?.error || 'Snyk scan failed');
    }

    if (scanResults.deepsource && scanResults.deepsource.success) {
        displayDeepSourceResults(scanResults.deepsource);
    } else {
        displayError('deepsource', scanResults.deepsource?.error || 'DeepSource scan failed');
    }
}

function displaySnykResults(result) {
    const metrics = result.metrics || {};
    const advanced = result.advanced_metrics || {};

    console.log('Snyk Result:', result);
    console.log('Snyk Advanced Metrics:', advanced);

    document.getElementById('snykStatus').textContent = 'Success';
    document.getElementById('snykStatus').className = 'status-badge success';
    document.getElementById('snykCritical').textContent = metrics.critical || 0;
    document.getElementById('snykHigh').textContent = metrics.high || 0;
    document.getElementById('snykMedium').textContent = metrics.medium || 0;
    document.getElementById('snykLow').textContent = metrics.low || 0;
    document.getElementById('snykTotal').textContent = metrics.total_issues || 0;
    document.getElementById('snykDuration').textContent = `${(metrics.scan_duration || 0).toFixed(2)}s`;

    window.snykDetails = {
        metrics: metrics,
        advanced: advanced,
        rawData: result
    };
}

function displayDeepSourceResults(result) {
    const metrics = result.metrics || {};
    const advanced = result.advanced_metrics || {};

    console.log('DeepSource Result:', result);
    console.log('DeepSource Advanced Metrics:', advanced);

    document.getElementById('deepsourceStatus').textContent = 'Success';
    document.getElementById('deepsourceStatus').className = 'status-badge success';
    document.getElementById('deepsourceCritical').textContent = metrics.critical || 0;
    document.getElementById('deepsourceHigh').textContent = metrics.high || 0;
    document.getElementById('deepsourceMedium').textContent = metrics.medium || 0;
    document.getElementById('deepsourceLow').textContent = metrics.low || 0;
    document.getElementById('deepsourceTotal').textContent = metrics.total_issues || 0;
    document.getElementById('deepsourceDuration').textContent = `${(metrics.scan_duration || 0).toFixed(2)}s`;

    window.deepsourceDetails = {
        metrics: metrics,
        advanced: advanced,
        rawData: result
    };
}

function displayError(tool, errorMessage) {
    const statusElement = document.getElementById(`${tool}Status`);
    if (statusElement) {
        statusElement.textContent = 'Error';
        statusElement.className = 'status-badge error';
        statusElement.title = errorMessage;
    }
    
    ['Critical', 'High', 'Medium', 'Low', 'Total'].forEach(level => {
        const element = document.getElementById(`${tool}${level}`);
        if (element) element.textContent = '0';
    });
    
    console.error(`${tool} error:`, errorMessage);
    
    const snykCliHint =
        errorMessage &&
        (errorMessage.includes('Snyk CLI') ||
            errorMessage.includes('Snyk CLI bulunamadı'));
    if (snykCliHint) {
        console.warn('To install Snyk CLI:');
        console.warn('  1. npm install -g snyk');
        console.warn('  2. snyk auth');
        console.warn('  3. Check SNYK_PATH in backend/metric_runner.py if needed');
    }
}

function buildCompactMetricTable(rows) {
    let html = '<table class="issue-table issue-table--compact"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>';
    for (const [label, value] of rows) {
        html += `<tr><td>${label}</td><td>${value}</td></tr>`;
    }
    html += '</tbody></table>';
    return html;
}

function detailMetricPanel(title, innerHtml, muted = false) {
    const mutedClass = muted ? ' detail-metric-panel--muted' : '';
    return `<section class="detail-metric-panel${mutedClass}"><h4 class="detail-metric-panel__title">${title}</h4><div class="detail-metric-panel__body">${innerHtml}</div></section>`;
}

function showDetails(tool) {
    const modal = document.getElementById('detailsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    const details = window[`${tool}Details`];

    if (!details) {
        alert('No detailed data available.');
        return;
    }

    console.log(`${tool} Details:`, details);
    console.log(`${tool} Advanced:`, details.advanced);

    modalTitle.textContent = `${tool === 'snyk' ? 'Snyk Code' : 'DeepSource'} — Detailed results`;

    const m = details.metrics || {};
    const coreRows = [
        ['Total issues', m.total_issues ?? 0],
        ['Critical', m.critical ?? 0],
        ['High', m.high ?? 0],
        ['Medium', m.medium ?? 0],
        ['Low', m.low ?? 0],
        ['Scan duration', `${(m.scan_duration || 0).toFixed(2)}s`]
    ];
    const corePanel = detailMetricPanel('Core metrics', buildCompactMetricTable(coreRows));

    let defectPanel;
    let coveragePanel;
    let opsPanel;

    if (details.advanced && Object.keys(details.advanced).length > 0) {
        const accuracy = details.advanced.defect_detection_accuracy || {};
        const falsePositiveRate = details.advanced.false_positive_rate !== undefined
            ? details.advanced.false_positive_rate
            : (accuracy.false_positive_rate || 0);

        const defectRows = [
            ['Precision', `${((accuracy.precision || 0) * 100).toFixed(2)}%`],
            ['Recall', `${((accuracy.recall || 0) * 100).toFixed(2)}%`],
            ['F1 score', `${((accuracy.f1_score || 0) * 100).toFixed(2)}%`],
            ['True positives', accuracy.true_positives ?? 0],
            ['False positives', accuracy.false_positives ?? 0],
            ['False negatives', accuracy.false_negatives ?? 0],
            ['False positive rate', `${(falsePositiveRate * 100).toFixed(2)}%`]
        ];
        defectPanel = detailMetricPanel('Defect detection', buildCompactMetricTable(defectRows));

        const coverage = details.advanced.code_coverage || {};
        const coverageRows = [
            ['Code coverage', `${(coverage.code_coverage_percent || 0).toFixed(2)}%`],
            ['Files analyzed', coverage.files_analyzed ?? 0],
            ['Lines analyzed', coverage.lines_analyzed ?? 0]
        ];
        coveragePanel = detailMetricPanel('Code coverage', buildCompactMetricTable(coverageRows));

        const efficiency = details.advanced.operational_efficiency || {};
        const opsRows = [
            ['Average scan time', `${(efficiency.average_scan_time || 0).toFixed(2)}s`],
            ['CPU usage', `${(efficiency.cpu_usage_percent || 0).toFixed(2)}%`],
            ['Memory usage', `${(efficiency.memory_usage_mb !== undefined ? efficiency.memory_usage_mb : 0).toFixed(2)} MB`]
        ];
        if (details.advanced.code_quality_score !== null && details.advanced.code_quality_score !== undefined) {
            opsRows.push(['Code quality score', details.advanced.code_quality_score.toFixed(2)]);
        }
        opsPanel = detailMetricPanel('Operations & quality', buildCompactMetricTable(opsRows));
    } else {
        const emptyMsg =
            '<p class="detail-metric-panel__empty">Advanced metrics not computed. Ground truth is required for precision, recall, and F1.</p>';
        defectPanel = detailMetricPanel('Defect detection', emptyMsg, true);
        coveragePanel = detailMetricPanel('Code coverage', '<p class="detail-metric-panel__empty">N/A</p>', true);
        opsPanel = detailMetricPanel('Operations & quality', '<p class="detail-metric-panel__empty">N/A</p>', true);
    }

    const html = `<div class="details-content"><div class="details-metrics-grid">${corePanel}${defectPanel}${coveragePanel}${opsPanel}</div></div>`;

    modalBody.innerHTML = html;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('detailsModal');
    modal.style.display = 'none';
}

function showError(message) {
    loadingState.style.display = 'none';
    resultsContainer.style.display = 'none';
    errorState.style.display = 'block';
    errorMessage.textContent = message;
}

function resetScan() {
    uploadedFiles = [];
    scanResults = {};
    fileList.style.display = 'none';
    fileListItems.innerHTML = '';
    scanButton.disabled = true;
    uploadSection.style.display = '';
    resultsSection.style.display = 'none';
    errorState.style.display = 'none';
    fileInput.value = '';
    
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.className = 'scan-step';
            const icon = step.querySelector('.step-icon');
            icon.textContent = '⏳';
        }
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        closeModal();
    }
}
