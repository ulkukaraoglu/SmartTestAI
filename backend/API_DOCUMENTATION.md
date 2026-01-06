# SmartTestAI API Dokümantasyonu

## Genel Bilgiler

**Base URL:** `http://localhost:5001`

**Content-Type:** `application/json`

---

## Endpoint'ler

### 1. Code Taraması (Tek Proje)

**Endpoint:** `POST /scan/code`

**Açıklama:** Belirli bir test projesi için Snyk Code taraması yapar.

**Request Body (JSON):**
```json
{
  "project": "flask_demo"
}
```

**Query Parameter (Alternatif):**
```
POST /scan/code?project=flask_demo
```

**Parametreler:**
- `project` (string, opsiyonel): Test projesi adı
  - `flask_demo` (default)
  - `nodejs-goof`

**Response (Başarılı - 200):**
```json
{
  "message": "code scan completed",
  "project": "flask_demo",
  "file_path": "../results/snyk_code_flask_demo_2026-01-02_15-30-45.json",
  "metrics": {
    "tool_name": "Snyk Code",
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 3,
    "total_issues": 10,
    "scan_duration": 12.5
  }
}
```

**Response (Hata - 400):**
```json
{
  "error": "Invalid project. Available projects: ['flask_demo', 'nodejs-goof']",
  "available_projects": ["flask_demo", "nodejs-goof"]
}
```

**Örnek Kullanım (cURL):**
```bash
# JSON body ile
curl -X POST http://localhost:5001/scan/code \
  -H "Content-Type: application/json" \
  -d '{"project": "flask_demo"}'

# Query parameter ile
curl -X POST "http://localhost:5001/scan/code?project=nodejs-goof"
```

---

### 2. Code Taraması (Tüm Projeler)

**Endpoint:** `POST /scan/code/all`

**Açıklama:** Tüm test projeleri için code taraması yapar.

**Request Body:** Yok

**Response (200):**
```json
{
  "message": "Scanned 2/2 projects",
  "results": [
    {
      "success": true,
      "project": "flask_demo",
      "file_path": "../results/snyk_code_flask_demo_2026-01-02_15-30-45.json",
      "metric_result": {
        "tool_name": "Snyk Code",
        "critical": 0,
        "high": 2,
        "medium": 5,
        "low": 3,
        "total_issues": 10,
        "scan_duration": 12.5
      }
    },
    {
      "success": true,
      "project": "nodejs-goof",
      "file_path": "../results/snyk_code_nodejs-goof_2026-01-02_15-31-20.json",
      "metric_result": {
        "tool_name": "Snyk Code",
        "critical": 1,
        "high": 5,
        "medium": 8,
        "low": 4,
        "total_issues": 18,
        "scan_duration": 15.2
      }
    }
  ]
}
```

**Örnek Kullanım:**
```bash
curl -X POST http://localhost:5001/scan/code/all
```

---

### 3. Projeleri Listele

**Endpoint:** `GET /projects`

**Açıklama:** Mevcut test projelerini listeler.

**Response (200):**
```json
{
  "available_projects": ["flask_demo", "nodejs-goof"],
  "projects": [
    {
      "name": "flask_demo",
      "exists": true,
      "path": "../test_projects/flask_demo"
    },
    {
      "name": "nodejs-goof",
      "exists": true,
      "path": "../test_projects/nodejs-goof"
    }
  ]
}
```

**Örnek Kullanım:**
```bash
curl http://localhost:5001/projects
```

---

### 4. Container Taraması (Eski Endpoint)

**Endpoint:** `POST /scan`

**Açıklama:** Container taraması yapar (geriye dönük uyumluluk için).

**Response:**
```json
{
  "message": "scan completed",
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 1
  },
  "report_file": "reports/snyk-report-2026-01-02_15-30-45.json"
}
```

---

## Test Senaryoları

### Senaryo 1: Flask Demo Projesi Taraması

**Amaç:** Flask tabanlı Python uygulamasında güvenlik açıklarını tespit etmek.

**Test Projesi:** `flask_demo`

**Çalıştırma:**
```bash
curl -X POST http://localhost:5001/scan/code \
  -H "Content-Type: application/json" \
  -d '{"project": "flask_demo"}'
```

**Beklenen Sonuç:**
- JSON çıktısı `results/` klasörüne kaydedilir
- Metrik sonuçları döner (critical, high, medium, low sayıları)
- Tarama süresi ölçülür

---

### Senaryo 2: Node.js Goof Projesi Taraması

**Amaç:** Node.js uygulamasında bilinen güvenlik açıklarını tespit etmek.

**Test Projesi:** `nodejs-goof`

**Çalıştırma:**
```bash
curl -X POST http://localhost:5001/scan/code \
  -H "Content-Type: application/json" \
  -d '{"project": "nodejs-goof"}'
```

**Beklenen Sonuç:**
- JSON çıktısı `results/` klasörüne kaydedilir
- Daha fazla güvenlik açığı bulunması beklenir (goof projesi kasıtlı olarak açıklı içerir)
- Metrik sonuçları döner

---

### Senaryo 3: Tüm Projeleri Tarama

**Amaç:** Her iki test projesini de otomatik olarak taramak.

**Çalıştırma:**
```bash
curl -X POST http://localhost:5001/scan/code/all
```

**Beklenen Sonuç:**
- Her iki proje için tarama yapılır
- Her proje için ayrı JSON dosyası oluşturulur
- Tüm sonuçlar tek bir response'da döner

---

## Hata Yönetimi

### Geçersiz Proje Adı
```json
{
  "error": "Invalid project. Available projects: ['flask_demo', 'nodejs-goof']",
  "available_projects": ["flask_demo", "nodejs-goof"]
}
```

### Tarama Hatası
```json
{
  "error": "Project 'invalid_project' not found in test_projects/",
  "project": "invalid_project"
}
```

---

## Sonuç Dosyaları

Tüm tarama sonuçları `results/` klasörüne kaydedilir.

**Dosya İsimlendirme Formatı:**
```
snyk_code_{project_name}_{timestamp}.json
```

**Örnek:**
- `snyk_code_flask_demo_2026-01-02_15-30-45.json`
- `snyk_code_nodejs-goof_2026-01-02_15-31-20.json`

---

## Python ile Kullanım Örneği

```python
import requests

# Tek proje taraması
response = requests.post(
    "http://localhost:5001/scan/code",
    json={"project": "flask_demo"}
)
print(response.json())

# Tüm projeleri tarama
response = requests.post("http://localhost:5001/scan/code/all")
results = response.json()
for result in results["results"]:
    if result["success"]:
        print(f"{result['project']}: {result['metric_result']['total_issues']} issues found")
```

---

## Notlar

- API çalışırken backend klasöründe olmalısınız
- Snyk CLI'nin kurulu ve yapılandırılmış olması gerekir
- Test projeleri `test_projects/` klasöründe olmalıdır
- Port 5001 varsayılan olarak kullanılır

