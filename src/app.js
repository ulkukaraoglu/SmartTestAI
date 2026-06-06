// API base URL — same origin as the backend
const API_BASE_URL = window.location.origin;

// Global state
let uploadedFiles = [];
let scanResults = {};
let lastDetailsTool = null;

// ----- Internationalization (i18n) -----
const translations = {
    en: {
        subtitle: 'Compare AI-Powered Code Analysis Tools',
        upload_title: '📁 Upload Files',
        upload_desc: 'Upload the Python file to analyze (or a ZIP archive)',
        upload_drag: '<strong>Drag files here</strong> or click to browse',
        upload_formats: 'Supported formats: .py, .js, .java, .cpp, .c, .go, .rs, .txt, .zip',
        uploading: 'Uploading...',
        uploaded_files: 'Uploaded files:',
        start_scan: '🔍 Start scan',
        results_title: '📊 Scan results',
        scanning: 'Scanning... This may take a few minutes.',
        step1: 'Uploading files...',
        step2: 'Snyk Code scan...',
        step3: 'DeepSource scan...',
        step4: 'Preparing results...',
        status_success: 'Success',
        status_error: 'Error',
        critical: 'Critical',
        high: 'High',
        medium: 'Medium',
        low: 'Low',
        total_issues_label: 'Total issues:',
        scan_duration_label: 'Scan duration:',
        show_details: 'Show details',
        detailed_results: 'Detailed results',
        error_title: 'Something went wrong',
        try_again: 'Try again',
        footer: 'SmartTestAI — AI code analysis tools benchmark',
        // dynamic
        details_suffix: 'Detailed results',
        panel_core: 'Core metrics',
        panel_defect: 'Defect detection',
        panel_coverage: 'Code coverage',
        panel_ops: 'Operations & quality',
        col_metric: 'Metric',
        col_value: 'Value',
        m_total_issues: 'Total issues',
        m_scan_duration: 'Scan duration',
        m_precision: 'Precision',
        m_recall: 'Recall',
        m_f1: 'F1 score',
        m_true_positives: 'True positives',
        m_false_positives: 'False positives',
        m_false_negatives: 'False negatives',
        m_false_positive_rate: 'False positive rate',
        m_code_coverage: 'Code coverage',
        m_files_analyzed: 'Files analyzed',
        m_lines_analyzed: 'Lines analyzed',
        m_avg_scan_time: 'Average scan time',
        m_cpu_usage: 'CPU usage',
        m_memory_usage: 'Memory usage',
        m_code_quality: 'Code quality score',
        empty_advanced: 'Advanced metrics not computed. Ground truth is required for precision, recall, and F1.',
        empty_na: 'N/A',
        alert_no_files: 'Please upload at least one file first.',
        alert_no_details: 'No detailed data available.'
    },
    tr: {
        subtitle: 'Yapay Zeka Destekli Kod Analiz Araçlarını Karşılaştırın',
        upload_title: '📁 Dosya Yükle',
        upload_desc: 'Analiz edilecek Python dosyasını (veya ZIP arşivini) yükleyin',
        upload_drag: '<strong>Dosyaları buraya sürükleyin</strong> ya da tıklayarak seçin',
        upload_formats: 'Desteklenen formatlar: .py, .js, .java, .cpp, .c, .go, .rs, .txt, .zip',
        uploading: 'Yükleniyor...',
        uploaded_files: 'Yüklenen dosyalar:',
        start_scan: '🔍 Taramayı başlat',
        results_title: '📊 Tarama sonuçları',
        scanning: 'Taranıyor... Bu birkaç dakika sürebilir.',
        step1: 'Dosyalar yükleniyor...',
        step2: 'Snyk Code taraması...',
        step3: 'DeepSource taraması...',
        step4: 'Sonuçlar hazırlanıyor...',
        status_success: 'Başarılı',
        status_error: 'Hata',
        critical: 'Kritik',
        high: 'Yüksek',
        medium: 'Orta',
        low: 'Düşük',
        total_issues_label: 'Toplam sorun:',
        scan_duration_label: 'Tarama süresi:',
        show_details: 'Detayları göster',
        detailed_results: 'Detaylı sonuçlar',
        error_title: 'Bir şeyler ters gitti',
        try_again: 'Tekrar dene',
        footer: 'SmartTestAI — Yapay zeka kod analiz araçları kıyaslaması',
        // dynamic
        details_suffix: 'Detaylı sonuçlar',
        panel_core: 'Temel metrikler',
        panel_defect: 'Hata tespiti',
        panel_coverage: 'Kod kapsamı',
        panel_ops: 'Operasyon & kalite',
        col_metric: 'Metrik',
        col_value: 'Değer',
        m_total_issues: 'Toplam sorun',
        m_scan_duration: 'Tarama süresi',
        m_precision: 'Kesinlik (Precision)',
        m_recall: 'Duyarlılık (Recall)',
        m_f1: 'F1 skoru',
        m_true_positives: 'Doğru pozitif',
        m_false_positives: 'Yanlış pozitif',
        m_false_negatives: 'Yanlış negatif',
        m_false_positive_rate: 'Yanlış pozitif oranı',
        m_code_coverage: 'Kod kapsamı',
        m_files_analyzed: 'Analiz edilen dosya',
        m_lines_analyzed: 'Analiz edilen satır',
        m_avg_scan_time: 'Ortalama tarama süresi',
        m_cpu_usage: 'CPU kullanımı',
        m_memory_usage: 'Bellek kullanımı',
        m_code_quality: 'Kod kalite puanı',
        empty_advanced: 'Gelişmiş metrikler hesaplanmadı. Kesinlik, duyarlılık ve F1 için ground truth gerekir.',
        empty_na: 'Yok',
        alert_no_files: 'Lütfen önce en az bir dosya yükleyin.',
        alert_no_details: 'Detaylı veri bulunmuyor.'
    }
};

let currentLang = localStorage.getItem('lang') || 'en';

function t(key) {
    const lang = translations[currentLang] ? currentLang : 'en';
    return (translations[lang] && translations[lang][key]) || translations.en[key] || key;
}

function applyTranslations() {
    document.documentElement.lang = currentLang;

    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        el.innerHTML = t(el.getAttribute('data-i18n-html'));
    });

    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === currentLang);
    });

    // Re-render the details modal if it is currently open
    const modal = document.getElementById('detailsModal');
    if (modal && modal.style.display === 'flex' && lastDetailsTool) {
        showDetails(lastDetailsTool);
    }
}

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyTranslations();
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => setLanguage(btn.getAttribute('data-lang')));
    });
    applyTranslations();
});

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
        alert(t('alert_no_files'));
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

    const snykStatusEl = document.getElementById('snykStatus');
    snykStatusEl.dataset.i18n = 'status_success';
    snykStatusEl.textContent = t('status_success');
    snykStatusEl.className = 'status-badge success';
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

    const deepsourceStatusEl = document.getElementById('deepsourceStatus');
    deepsourceStatusEl.dataset.i18n = 'status_success';
    deepsourceStatusEl.textContent = t('status_success');
    deepsourceStatusEl.className = 'status-badge success';
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
        statusElement.dataset.i18n = 'status_error';
        statusElement.textContent = t('status_error');
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
    let html = `<table class="issue-table issue-table--compact"><thead><tr><th>${t('col_metric')}</th><th>${t('col_value')}</th></tr></thead><tbody>`;
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
        alert(t('alert_no_details'));
        return;
    }

    lastDetailsTool = tool;

    console.log(`${tool} Details:`, details);
    console.log(`${tool} Advanced:`, details.advanced);

    modalTitle.removeAttribute('data-i18n');
    modalTitle.textContent = `${tool === 'snyk' ? 'Snyk Code' : 'DeepSource'} — ${t('details_suffix')}`;

    const m = details.metrics || {};
    const coreRows = [
        [t('m_total_issues'), m.total_issues ?? 0],
        [t('critical'), m.critical ?? 0],
        [t('high'), m.high ?? 0],
        [t('medium'), m.medium ?? 0],
        [t('low'), m.low ?? 0],
        [t('m_scan_duration'), `${(m.scan_duration || 0).toFixed(2)}s`]
    ];
    const corePanel = detailMetricPanel(t('panel_core'), buildCompactMetricTable(coreRows));

    let defectPanel;
    let coveragePanel;
    let opsPanel;

    if (details.advanced && Object.keys(details.advanced).length > 0) {
        const accuracy = details.advanced.defect_detection_accuracy || {};
        const falsePositiveRate = details.advanced.false_positive_rate !== undefined
            ? details.advanced.false_positive_rate
            : (accuracy.false_positive_rate || 0);

        const defectRows = [
            [t('m_precision'), `${((accuracy.precision || 0) * 100).toFixed(2)}%`],
            [t('m_recall'), `${((accuracy.recall || 0) * 100).toFixed(2)}%`],
            [t('m_f1'), `${((accuracy.f1_score || 0) * 100).toFixed(2)}%`],
            [t('m_true_positives'), accuracy.true_positives ?? 0],
            [t('m_false_positives'), accuracy.false_positives ?? 0],
            [t('m_false_negatives'), accuracy.false_negatives ?? 0],
            [t('m_false_positive_rate'), `${(falsePositiveRate * 100).toFixed(2)}%`]
        ];
        defectPanel = detailMetricPanel(t('panel_defect'), buildCompactMetricTable(defectRows));

        const coverage = details.advanced.code_coverage || {};
        const coverageRows = [
            [t('m_code_coverage'), `${(coverage.code_coverage_percent || 0).toFixed(2)}%`],
            [t('m_files_analyzed'), coverage.files_analyzed ?? 0],
            [t('m_lines_analyzed'), coverage.lines_analyzed ?? 0]
        ];
        coveragePanel = detailMetricPanel(t('panel_coverage'), buildCompactMetricTable(coverageRows));

        const efficiency = details.advanced.operational_efficiency || {};
        const opsRows = [
            [t('m_avg_scan_time'), `${(efficiency.average_scan_time || 0).toFixed(2)}s`],
            [t('m_cpu_usage'), `${(efficiency.cpu_usage_percent || 0).toFixed(2)}%`],
            [t('m_memory_usage'), `${(efficiency.memory_usage_mb !== undefined ? efficiency.memory_usage_mb : 0).toFixed(2)} MB`]
        ];
        if (details.advanced.code_quality_score !== null && details.advanced.code_quality_score !== undefined) {
            opsRows.push([t('m_code_quality'), details.advanced.code_quality_score.toFixed(2)]);
        }
        opsPanel = detailMetricPanel(t('panel_ops'), buildCompactMetricTable(opsRows));
    } else {
        const emptyMsg =
            `<p class="detail-metric-panel__empty">${t('empty_advanced')}</p>`;
        defectPanel = detailMetricPanel(t('panel_defect'), emptyMsg, true);
        coveragePanel = detailMetricPanel(t('panel_coverage'), `<p class="detail-metric-panel__empty">${t('empty_na')}</p>`, true);
        opsPanel = detailMetricPanel(t('panel_ops'), `<p class="detail-metric-panel__empty">${t('empty_na')}</p>`, true);
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
