# SmartTestAI - Hızlı Başlangıç Rehberi

Bu rehber, SmartTestAI projesini çalıştırmak için gerekli adımları içerir.

## 📋 Gereksinimler

- Python 3.8+
- Flask, requests, psutil paketleri kurulu
- Snyk CLI (Snyk Code taraması için - opsiyonel)
- DeepSource API Token (DeepSource taraması için - opsiyonel, mock mod mevcut)

## 🚀 Hızlı Başlangıç

### ADIM 1: Gerekli Paketleri Kurun

```powershell
cd backend
pip install flask requests psutil
```

### ADIM 2: API'yi Başlatın

**Terminal 1'de (backend klasöründe):**

```powershell
cd backend
python app.py
```

API başarıyla çalıştığında şunu göreceksiniz:
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

**⚠️ ÖNEMLİ:** API'yi durdurmadan Terminal 2'ye geçin!

### ADIM 3: Test Endpoint'lerini Çalıştırın

**Terminal 2'de (yeni PowerShell penceresi):**

#### 3.1. Mevcut Projeleri Listele

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/projects" -Method GET | ConvertTo-Json
```

#### 3.2. Snyk Code Taraması (flask_demo)

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/scan/code" -Method POST -ContentType "application/json" -Body '{"project": "flask_demo"}' | ConvertTo-Json -Depth 10
```

**Çıktı:**
- Temel metrikler
- Advanced metrics
- 2 dosya oluşturulur:
  - `results/snyk_code_flask_demo_[timestamp].json` (temel metrikler)
  - `results/snyk_code_advanced_metrics_flask_demo_[timestamp].json` (advanced metrics)

#### 3.3. DeepSource Taraması (flask_demo)

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/scan/deepsource" -Method POST -ContentType "application/json" -Body '{"project": "flask_demo"}' | ConvertTo-Json -Depth 10
```

**Çıktı:**
- Temel metrikler
- Advanced metrics
- 2 dosya oluşturulur:
  - `results/deepsource_flask_demo_[timestamp].json` (temel metrikler)
  - `results/deepsource_advanced_metrics_flask_demo_[timestamp].json` (advanced metrics)

#### 3.4. Tüm Projeleri Tara (Snyk Code)

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/scan/code/all" -Method POST | ConvertTo-Json -Depth 10
```

#### 3.5. Tüm Projeleri Tara (DeepSource)

```powershell
Invoke-RestMethod -Uri "http://localhost:5001/scan/deepsource/all" -Method POST | ConvertTo-Json -Depth 10
```

### ADIM 4: Sonuç Dosyalarını Kontrol Edin

```powershell
Get-ChildItem results | Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name, LastWriteTime
```

Son 10 sonuç dosyasını gösterir.

## 📁 Oluşturulan Dosyalar

Her tarama işlemi **2 dosya** oluşturur:

### Snyk Code için:
1. **Temel Metrikler:** `snyk_code_flask_demo_[timestamp].json`
   - Critical, High, Medium, Low issue sayıları
   - Total issues
   - Scan duration

2. **Advanced Metrics:** `snyk_code_advanced_metrics_flask_demo_[timestamp].json`
   - Defect Detection Accuracy (Precision, Recall, F1 Score)
   - Code Coverage
   - Operational Efficiency (CPU, Memory, Scan Time)

### DeepSource için:
1. **Temel Metrikler:** `deepsource_flask_demo_[timestamp].json`
   - Critical, High, Medium, Low issue sayıları
   - Total issues
   - Scan duration

2. **Advanced Metrics:** `deepsource_advanced_metrics_flask_demo_[timestamp].json`
   - Defect Detection Accuracy (Precision, Recall, F1 Score)
   - Code Coverage
   - Operational Efficiency (CPU, Memory, Scan Time)

## 🔧 Yapılandırma

### Snyk CLI (Opsiyonel)

Snyk Code taraması için Snyk CLI kurulu olmalı:

```powershell
npm install -g snyk
snyk auth
```

Snyk CLI yolunu `backend/metric_runner.py` dosyasında güncelleyin:
```python
SNYK_PATH = r"C:\Users\YOUR_USERNAME\AppData\Roaming\npm\snyk.cmd"
```

### DeepSource API Token (Opsiyonel)

DeepSource API token'ı ayarlayın:

```powershell
$env:DEEPSOURCE_API_TOKEN="your_token_here"
$env:DEEPSOURCE_REPO_OWNER="github_username"
$env:DEEPSOURCE_REPO_NAME="repository_name"
```

Token olmadan da çalışır (mock mod kullanılır).

## 📊 API Response Formatı

Her endpoint şu formatta response döner:

```json
{
  "message": "code scan completed",
  "project": "flask_demo",
  "file_path": "../results/snyk_code_flask_demo_...json",
  "advanced_metrics_file_path": "../results/snyk_code_advanced_metrics_flask_demo_...json",
  "metrics": {
    "tool_name": "Snyk Code",
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "total_issues": 0,
    "scan_duration": 0.0
  },
  "advanced_metrics": {
    "defect_detection_accuracy": { ... },
    "code_coverage": { ... },
    "operational_efficiency": { ... }
  }
}
```

## 🐛 Sorun Giderme

### API Başlamıyor
- Python'un kurulu olduğundan emin olun: `python --version`
- Gerekli paketlerin kurulu olduğundan emin olun: `pip install flask requests psutil`
- Port 5001'in boş olduğundan emin olun

### Snyk Taraması Başarısız
- Snyk CLI'nin kurulu olduğundan emin olun: `snyk --version`
- Snyk CLI yolunun doğru olduğundan emin olun (`backend/metric_runner.py`)

### DeepSource Mock Mod
- API token yoksa otomatik olarak mock mod kullanılır
- Mock mod gerçek repository verileri yerine test verisi döner

## 📚 Daha Fazla Bilgi

- Detaylı API dokümantasyonu: `backend/API_DOCUMENTATION.md`
- Metrik dokümantasyonu: `backend/METRICS_DOCUMENTATION.md`
- Ana README: `README.md`

