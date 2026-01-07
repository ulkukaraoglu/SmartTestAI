// API Base URL - Backend ile aynı port'tan servis ediliyor
const API_BASE_URL = window.location.origin;

// Global state
let uploadedFiles = [];
let scanResults = {};

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const fileList = document.getElementById('fileList');
const fileListItems = document.getElementById('fileListItems');
const scanButton = document.getElementById('scanButton');
const resultsSection = document.getElementById('resultsSection');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('resultsContainer');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
scanButton.addEventListener('click', startScan);

// Drag and Drop Handlers
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

// Scan Functions
async function startScan() {
    if (uploadedFiles.length === 0) {
        alert('Lütfen önce dosya yükleyin!');
        return;
    }

    // Reset UI
    scanButton.disabled = true;
    resultsSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsContainer.style.display = 'none';
    errorState.style.display = 'none';

    try {
        // Step 1: Upload files
        updateScanStep(1, 'active');
        const projectName = await uploadFiles();
        updateScanStep(1, 'completed');
        
        // Step 2: Snyk Code scan
        updateScanStep(2, 'active');
        const snykResult = await runSnykScan(projectName);
        updateScanStep(2, 'completed');
        
        // Step 3: DeepSource scan
        updateScanStep(3, 'active');
        const deepsourceResult = await runDeepSourceScan(projectName);
        updateScanStep(3, 'completed');
        
        // Step 4: Process results
        updateScanStep(4, 'active');
        scanResults = {
            snyk: snykResult,
            deepsource: deepsourceResult
        };
        updateScanStep(4, 'completed');
        
        // Display results
        displayResults();
        
    } catch (error) {
        console.error('Scan error:', error);
        showError(error.message || 'Tarama sırasında bir hata oluştu!');
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
            throw new Error(`Dosya yükleme hatası: ${response.statusText}`);
        }

        const result = await response.json();
        return result.project_name;
    } catch (error) {
        throw new Error(`Dosya yüklenemedi: ${error.message}`);
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
            throw new Error(`Snyk tarama hatası: ${errorMsg}`);
        }
        
        if (!result.success) {
            const errorMsg = result.error || 'Snyk taraması başarısız';
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
            throw new Error(`DeepSource tarama hatası: ${errorMsg}`);
        }
        
        if (!result.success) {
            const errorMsg = result.error || 'DeepSource taraması başarısız';
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

    // Display Snyk results
    if (scanResults.snyk && scanResults.snyk.success) {
        displaySnykResults(scanResults.snyk);
    } else {
        displayError('snyk', scanResults.snyk?.error || 'Snyk taraması başarısız');
    }

    // Display DeepSource results
    if (scanResults.deepsource && scanResults.deepsource.success) {
        displayDeepSourceResults(scanResults.deepsource);
    } else {
        displayError('deepsource', scanResults.deepsource?.error || 'DeepSource taraması başarısız');
    }

    // Display advanced metrics
    displayAdvancedMetrics();
}

function displaySnykResults(result) {
    const metrics = result.metrics || {};
    const advanced = result.advanced_metrics || {};

    document.getElementById('snykStatus').textContent = 'Başarılı';
    document.getElementById('snykStatus').className = 'status-badge success';
    document.getElementById('snykCritical').textContent = metrics.critical || 0;
    document.getElementById('snykHigh').textContent = metrics.high || 0;
    document.getElementById('snykMedium').textContent = metrics.medium || 0;
    document.getElementById('snykLow').textContent = metrics.low || 0;
    document.getElementById('snykTotal').textContent = metrics.total_issues || 0;
    document.getElementById('snykDuration').textContent = `${(metrics.scan_duration || 0).toFixed(2)}s`;

    // Store detailed data for modal
    window.snykDetails = {
        metrics: metrics,
        advanced: advanced,
        rawData: result
    };
}

function displayDeepSourceResults(result) {
    const metrics = result.metrics || {};
    const advanced = result.advanced_metrics || {};

    document.getElementById('deepsourceStatus').textContent = 'Başarılı';
    document.getElementById('deepsourceStatus').className = 'status-badge success';
    document.getElementById('deepsourceCritical').textContent = metrics.critical || 0;
    document.getElementById('deepsourceHigh').textContent = metrics.high || 0;
    document.getElementById('deepsourceMedium').textContent = metrics.medium || 0;
    document.getElementById('deepsourceLow').textContent = metrics.low || 0;
    document.getElementById('deepsourceTotal').textContent = metrics.total_issues || 0;
    document.getElementById('deepsourceDuration').textContent = `${(metrics.scan_duration || 0).toFixed(2)}s`;

    // Store detailed data for modal
    window.deepsourceDetails = {
        metrics: metrics,
        advanced: advanced,
        rawData: result
    };
}

function displayError(tool, errorMessage) {
    const statusElement = document.getElementById(`${tool}Status`);
    if (statusElement) {
        statusElement.textContent = 'Hata';
        statusElement.className = 'status-badge error';
        // Hata mesajını tooltip olarak göster
        statusElement.title = errorMessage;
    }
    
    // Set all metrics to 0
    ['Critical', 'High', 'Medium', 'Low', 'Total'].forEach(level => {
        const element = document.getElementById(`${tool}${level}`);
        if (element) element.textContent = '0';
    });
    
    // Hata detaylarını console'a yazdır
    console.error(`${tool} error:`, errorMessage);
    
    // Eğer Snyk CLI bulunamadı hatası varsa, kullanıcıya yardım mesajı göster
    if (errorMessage && errorMessage.includes('Snyk CLI bulunamadı')) {
        console.warn('Snyk CLI kurulumu için:');
        console.warn('  1. npm install -g snyk');
        console.warn('  2. snyk auth');
        console.warn('  3. backend/metric_runner.py dosyasında SNYK_PATH değerini kontrol edin');
    }
}

function displayAdvancedMetrics() {
    // Snyk advanced metrics
    const snykAdvanced = scanResults.snyk?.advanced_metrics || {};
    const snykAccuracy = snykAdvanced.defect_detection_accuracy || {};
    
    if (snykAccuracy.precision !== undefined) {
        const precision = (snykAccuracy.precision * 100).toFixed(1);
        document.getElementById('snykPrecision').textContent = `${precision}%`;
        document.getElementById('snykPrecisionBar').style.width = `${precision}%`;
    }
    
    if (snykAccuracy.recall !== undefined) {
        const recall = (snykAccuracy.recall * 100).toFixed(1);
        document.getElementById('snykRecall').textContent = `${recall}%`;
        document.getElementById('snykRecallBar').style.width = `${recall}%`;
    }
    
    if (snykAccuracy.f1_score !== undefined) {
        const f1 = (snykAccuracy.f1_score * 100).toFixed(1);
        document.getElementById('snykF1').textContent = `${f1}%`;
        document.getElementById('snykF1Bar').style.width = `${f1}%`;
    }

    // DeepSource advanced metrics
    const deepsourceAdvanced = scanResults.deepsource?.advanced_metrics || {};
    const deepsourceAccuracy = deepsourceAdvanced.defect_detection_accuracy || {};
    
    if (deepsourceAccuracy.precision !== undefined) {
        const precision = (deepsourceAccuracy.precision * 100).toFixed(1);
        document.getElementById('deepsourcePrecision').textContent = `${precision}%`;
        document.getElementById('deepsourcePrecisionBar').style.width = `${precision}%`;
    }
    
    if (deepsourceAccuracy.recall !== undefined) {
        const recall = (deepsourceAccuracy.recall * 100).toFixed(1);
        document.getElementById('deepsourceRecall').textContent = `${recall}%`;
        document.getElementById('deepsourceRecallBar').style.width = `${recall}%`;
    }
    
    if (deepsourceAccuracy.f1_score !== undefined) {
        const f1 = (deepsourceAccuracy.f1_score * 100).toFixed(1);
        document.getElementById('deepsourceF1').textContent = `${f1}%`;
        document.getElementById('deepsourceF1Bar').style.width = `${f1}%`;
    }
}

function showDetails(tool) {
    const modal = document.getElementById('detailsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    const details = window[`${tool}Details`];
    
    if (!details) {
        alert('Detaylı bilgi bulunamadı!');
        return;
    }

    modalTitle.textContent = `${tool === 'snyk' ? 'Snyk Code' : 'DeepSource'} - Detaylı Sonuçlar`;
    
    let html = '<div class="details-content">';
    
    // Basic Metrics
    html += '<h3>Temel Metrikler</h3>';
    html += '<table class="issue-table">';
    html += '<tr><th>Metrik</th><th>Değer</th></tr>';
    html += `<tr><td>Toplam Issues</td><td>${details.metrics.total_issues || 0}</td></tr>`;
    html += `<tr><td>Critical</td><td>${details.metrics.critical || 0}</td></tr>`;
    html += `<tr><td>High</td><td>${details.metrics.high || 0}</td></tr>`;
    html += `<tr><td>Medium</td><td>${details.metrics.medium || 0}</td></tr>`;
    html += `<tr><td>Low</td><td>${details.metrics.low || 0}</td></tr>`;
    html += `<tr><td>Tarama Süresi</td><td>${(details.metrics.scan_duration || 0).toFixed(2)}s</td></tr>`;
    html += '</table>';
    
    // Advanced Metrics
    if (details.advanced) {
        html += '<h3 style="margin-top: 30px;">Gelişmiş Metrikler</h3>';
        
        const accuracy = details.advanced.defect_detection_accuracy || {};
        html += '<h4>Hata Tespit Başarısı</h4>';
        html += '<table class="issue-table">';
        html += '<tr><th>Metrik</th><th>Değer</th></tr>';
        html += `<tr><td>Precision</td><td>${((accuracy.precision || 0) * 100).toFixed(2)}%</td></tr>`;
        html += `<tr><td>Recall</td><td>${((accuracy.recall || 0) * 100).toFixed(2)}%</td></tr>`;
        html += `<tr><td>F1 Score</td><td>${((accuracy.f1_score || 0) * 100).toFixed(2)}%</td></tr>`;
        html += `<tr><td>True Positives</td><td>${accuracy.true_positives || 0}</td></tr>`;
        html += `<tr><td>False Positives</td><td>${accuracy.false_positives || 0}</td></tr>`;
        html += `<tr><td>False Negatives</td><td>${accuracy.false_negatives || 0}</td></tr>`;
        html += '</table>';
        
        const coverage = details.advanced.code_coverage || {};
        html += '<h4>Kod Kapsama</h4>';
        html += '<table class="issue-table">';
        html += '<tr><th>Metrik</th><th>Değer</th></tr>';
        html += `<tr><td>Code Coverage</td><td>${(coverage.code_coverage_percent || 0).toFixed(2)}%</td></tr>`;
        html += `<tr><td>Files Analyzed</td><td>${coverage.files_analyzed || 0}</td></tr>`;
        html += `<tr><td>Lines Analyzed</td><td>${coverage.lines_analyzed || 0}</td></tr>`;
        html += '</table>';
        
        const efficiency = details.advanced.operational_efficiency || {};
        html += '<h4>Operasyonel Verimlilik</h4>';
        html += '<table class="issue-table">';
        html += '<tr><th>Metrik</th><th>Değer</th></tr>';
        html += `<tr><td>Average Scan Time</td><td>${(efficiency.average_scan_time || 0).toFixed(2)}s</td></tr>`;
        html += `<tr><td>CPU Usage</td><td>${(efficiency.cpu_usage_percent || 0).toFixed(2)}%</td></tr>`;
        html += `<tr><td>Memory Usage</td><td>${(efficiency.memory_usage_mb || 0).toFixed(2)} MB</td></tr>`;
        html += '</table>';
    }
    
    html += '</div>';
    
    modalBody.innerHTML = html;
    modal.style.display = 'block';
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
    resultsSection.style.display = 'none';
    errorState.style.display = 'none';
    fileInput.value = '';
    
    // Reset scan steps
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.className = 'scan-step';
            const icon = step.querySelector('.step-icon');
            icon.textContent = '⏳';
        }
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        closeModal();
    }
}

