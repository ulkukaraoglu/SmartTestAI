# SmartTestAI - Feature Metrics Engine

Yapay zeka destekli kod analizi test araçlarını (AI Code Analysis Tools) aynı metrikler üzerinden ölçerek karşılaştıran bir benchmark sistemi.

## 🎯 Proje Amacı

"Hangi AI kod analiz aracı daha başarılı?" sorusuna ölçülebilir cevap vermek.

Bu projede şu an **SADECE KOD ANALİZİNE ODAKLANIYORUZ**.

## ✨ Özellikler

- ✅ **Çoklu Araç Desteği**: Snyk Code ve DeepSource entegrasyonu
- ✅ **Standart Metrik Formatı**: Tüm araçlar aynı metrik formatını kullanır
- ✅ **Gelişmiş Metrikler**: Precision, Recall, F1 Score, Code Coverage, False Positive Rate
- ✅ **RESTful API**: Flask tabanlı REST API ile kolay entegrasyon
- ✅ **Otomatik Normalizasyon**: Farklı araç çıktıları otomatik olarak normalize edilir
- ✅ **JSON Sonuç Kaydetme**: Tüm tarama sonuçları JSON formatında saklanır

## 🛠️ Desteklenen Araçlar

- ✅ **Snyk Code** - Statik kod analizi (SARIF format desteği)
- ✅ **DeepSource** - AI destekli kod analizi (GraphQL API entegrasyonu)

## 📁 Proje Yapısı

```
SmartTestAI-feature-metrics-engine/
├── backend/                       # Ana uygulama kodu
│   ├── app.py                     # Flask REST API (ana entry point)
│   ├── metric_runner.py           # Snyk Code runner
│   ├── deepsource_runner.py       # DeepSource runner
│   ├── metrics/                   # Metrik hesaplama modülleri
│   │   ├── base_metric.py         # Abstract metric class
│   │   ├── snyk_metrics.py        # Snyk metric implementation
│   │   ├── deepsource_metrics.py  # DeepSource metric implementation
│   │   ├── advanced_metrics.py    # Gelişmiş metrik hesaplama
│   │   └── result_model.py       # Standard metric result model
│   ├── tests/                     # Test script'leri
│   │   ├── test_advanced_metrics.py  # Gelişmiş metrik testleri
│   │   └── test_deepsource_api.py    # DeepSource API testleri
│   └── docs/                      # Backend dokümantasyonu
│       ├── API_DOCUMENTATION.md
│       └── METRICS_DOCUMENTATION.md
├── test_projects/                 # Test projeleri
│   ├── flask_demo/               # Flask test projesi
│   └── vulnerable_demo/          # Güvenlik açıklı test projesi
├── results/                       # Tarama sonuçları (JSON, gitignore'da)
└── README.md                      # Ana proje dokümantasyonu
```

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler

- Python 3.8+
- Snyk CLI (kurulu ve authenticate edilmiş)
- DeepSource API Token (opsiyonel, test modu mevcut)
- pip paketleri: `flask`, `requests`, `psutil`

### 2. Kurulum

```bash
# Repository'yi klonlayın
git clone <repository-url>
cd SmartTestAI-feature-metrics-engine

# Backend klasörüne gidin
cd backend

# Gerekli paketleri kurun
pip install flask requests psutil

# Snyk CLI'yi kurun (eğer kurulu değilse)
npm install -g snyk

# Snyk'i authenticate edin
snyk auth

# DeepSource API token'ı ayarlayın (opsiyonel)
export DEEPSOURCE_API_TOKEN="your_token_here"
```

### 3. API'yi Başlat

```bash
cd backend
python app.py
```

API `http://localhost:5001` adresinde çalışacak.

### 4. Test Senaryoları

**Snyk Code Taraması:**
```bash
curl -X POST http://localhost:5001/scan/code \
  -H "Content-Type: application/json" \
  -d '{"project": "flask_demo"}'
```

**DeepSource Taraması:**
```bash
curl -X POST http://localhost:5001/scan/deepsource \
  -H "Content-Type: application/json" \
  -d '{"project": "flask_demo"}'
```

**Gelişmiş Metrikleri Test Et:**
```bash
cd backend/tests
python test_advanced_metrics.py

# veya backend/ klasöründen:
cd backend
python -m tests.test_advanced_metrics
```

## 📊 Standart Metrik Formatı

Tüm araçlar aynı metrik formatını kullanır:

```json
{
  "tool_name": "Snyk Code" | "DeepSource",
  "critical": 0,
  "high": 0,
  "medium": 0,
  "low": 0,
  "total_issues": 0,
  "scan_duration": 0.0
}
```

### Severity Mapping

**Snyk Code:**
- Priority Score >= 900 → critical
- Priority Score >= 700 → high
- Priority Score >= 500 → medium
- Priority Score < 500 → low

**DeepSource:**
- CRITICAL → critical
- MAJOR → high
- MINOR → medium
- INFO → low

## 📈 Gelişmiş Metrikler

Gelişmiş metrikler şunları içerir:

1. **Defect Detection Accuracy (Hata Tespit Başarısı)**
   - Precision: Doğru pozitif / (Doğru pozitif + Yanlış pozitif)
   - Recall: Doğru pozitif / (Doğru pozitif + Yanlış negatif)
   - F1 Score: Precision ve Recall'un harmonik ortalaması
   - False Positive Rate: Yanlış pozitif / (Yanlış pozitif + Doğru negatif)

2. **Code Coverage (Kod Kapsama)**
   - Taranan kod satırı yüzdesi
   - Analiz edilen dosya sayısı
   - Analiz edilen satır sayısı

3. **Operational Efficiency (Operasyonel Verimlilik)**
   - Ortalama tarama süresi
   - CPU kullanım yüzdesi
   - Bellek kullanımı (MB)

## 🔗 API Endpoint'leri

### Snyk Code
- `POST /scan/code` - Tek proje taraması
- `POST /scan/code/all` - Tüm projeleri tarama

### DeepSource
- `POST /scan/deepsource` - Tek proje taraması
- `POST /scan/deepsource/all` - Tüm projeleri tarama

### Genel
- `GET /projects` - Mevcut projeleri listele

Detaylı API dokümantasyonu için: `backend/API_DOCUMENTATION.md`

## 🔧 Yapılandırma

### Snyk Code

Snyk CLI'nin kurulu ve authenticate edilmiş olması gerekir:

```bash
# Snyk CLI kurulumu
npm install -g snyk

# Authentication
snyk auth
```

**Not:** Organizasyon bilgileri `backend/metric_runner.py` dosyasında tanımlıdır ve tüm taramalarda otomatik kullanılır.

### DeepSource

DeepSource **bulut tabanlı ve repository'ye bağlı** çalışır: yerelde keyfi bir klasörü taramaz. Bir Git reposunu (GitHub/GitLab/Bitbucket) DeepSource'a bağlarsınız, repo her commit'te bulutta analiz edilir ve sonuçları GraphQL API'den çekersiniz.

> Bu projede `test_projects/` klasörü bu repoda olduğundan, repo DeepSource'a bağlıysa o projeler için **gerçek** DeepSource verisi çekilir. Web arayüzünden **yüklenen** dosyalar repoda olmadığından DeepSource onları doğrudan tarayamaz (bu durumda demo/mock veri ve uyarı gösterilir).

#### 1. Önkoşul: Repoyu DeepSource'a bağla

1. [https://app.deepsource.com](https://app.deepsource.com) adresine GitHub ile giriş yapın.
2. Bu repoyu (`SmartTestAI`) DeepSource üzerinde **aktive edin** (Add repository / Activate).
3. Repoda `.deepsource.toml` zaten mevcut (Python analyzer açık). İlk analiz, default branch'e bir commit attığınızda otomatik çalışır.

#### 2. Environment variable'ları nereden alırım?

| Değişken | Ne işe yarar | Nereden alınır |
|----------|--------------|----------------|
| `DEEPSOURCE_API_TOKEN` | GraphQL API'ye kimlik doğrulama (Personal Access Token / PAT) | DeepSource → sağ üst profil → **Settings → Access Tokens** (veya **API Access**) → **Generate / Create token**. Oluşan PAT'i kopyalayın (bir daha gösterilmez). |
| `DEEPSOURCE_REPO_OWNER` | Bağlı reponun sahibi (GitHub kullanıcı adı veya organizasyon) | Reponun GitHub URL'sinden: `github.com/<OWNER>/<NAME>` → buradaki `<OWNER>`. |
| `DEEPSOURCE_REPO_NAME` | Repo adı | Aynı URL'deki `<NAME>` (bu projede genellikle `SmartTestAI`). |
| `DEEPSOURCE_VCS_PROVIDER` | Sürüm kontrol sağlayıcısı | `GITHUB`, `GITLAB` veya `BITBUCKET` (büyük harf). |

#### 3. Değişkenleri ayarla ve başlat

**PowerShell (Windows):**
```powershell
$env:DEEPSOURCE_API_TOKEN="<DeepSource Personal Access Token>"
$env:DEEPSOURCE_REPO_OWNER="<github-kullanici-veya-org>"
$env:DEEPSOURCE_REPO_NAME="SmartTestAI"
$env:DEEPSOURCE_VCS_PROVIDER="GITHUB"
cd backend
python app.py
```

**cmd (Windows):**
```bat
set DEEPSOURCE_API_TOKEN=<token>
set DEEPSOURCE_REPO_OWNER=<owner>
set DEEPSOURCE_REPO_NAME=SmartTestAI
set DEEPSOURCE_VCS_PROVIDER=GITHUB
cd backend
python app.py
```

**Linux/Mac (bash):**
```bash
export DEEPSOURCE_API_TOKEN="<token>"
export DEEPSOURCE_REPO_OWNER="<owner>"
export DEEPSOURCE_REPO_NAME="SmartTestAI"
export DEEPSOURCE_VCS_PROVIDER="GITHUB"
cd backend
python app.py
```

> Alternatif olarak `backend/deepsource_runner.py` içindeki default değerleri (`DEEPSOURCE_REPO_OWNER`, `DEEPSOURCE_REPO_NAME`, `DEEPSOURCE_VCS_PROVIDER`) doğrudan düzenleyebilirsiniz; ancak token'ı koda yazmayın, environment variable kullanın.

#### 4. Çalışıyor mu kontrol et

```bash
curl -X POST http://localhost:5001/scan/deepsource \
  -H "Content-Type: application/json" \
  -d '{"project": "vulnerable_sql_injection"}'
```

Yanıtta `"scan_mode": "repository"` ve gerçek issue sayıları görüyorsanız canlı veri akıyordur. `"scan_mode": "mock"` görüyorsanız token/owner/name yanlış olabilir ya da repo o klasörü henüz analiz etmemiştir.

**API endpoint:** `https://api.deepsource.com/graphql/` (eski `api.deepsource.io` değil). Gerekirse `DEEPSOURCE_API_URL` ile özelleştirilebilir.

## 📝 Sonuç Dosyaları

Tüm tarama sonuçları `results/` klasörüne kaydedilir:

- **Temel Metrikler**: `{tool}_{project}_{timestamp}.json`
- **Gelişmiş Metrikler**: `{tool}_advanced_metrics_{project}_{timestamp}.json`

Örnek dosya adları:
- `snyk_code_flask_demo_2026-01-02_14-25-44.json`
- `deepsource_flask_demo_2026-01-02_17-34-46.json`
- `snyk_advanced_metrics_snyk_code_vulnerable_demo_2026-01-02_15-44-31_2026-01-02_17-26-17.json`

## 👥 Ekip Görevleri (Tamamlandı)

Tüm planlı iş paketleri tamamlandı.

### ✅ Kişi 1: Snyk Entegrasyonu
- Snyk Code taraması
- SARIF format desteği
- Metrik normalizasyonu

### ✅ Kişi 2: DeepSource Entegrasyonu
- DeepSource API entegrasyonu
- Metrik normalizasyonu
- Test modu desteği
- Gelişmiş metrik hesaplama

### ✅ Kişi 3: Otomasyon ve karşılaştırma
- `backend/benchmark_runner.py` — çalışan API üzerinden toplu tarama ve sonuç toplama
- `backend/comprehensive_test_report.py` — kapsamlı test raporu
- `backend/generate_html_report.py`, `backend/generate_analysis_report.py` — HTML / analiz raporu üretimi

### ✅ Kişi 4: Web arayüzü
- `src/` — dosya yükleme ve tarama akışı (`index.html`, `app.js`); backend `app.py` ile aynı origin’de (`http://localhost:5001/`) sunulur
- `POST /upload` ile kod yükleme; Snyk / DeepSource tarama sonuçlarının arayüzde gösterilmesi



## 📚 Dokümantasyon

- `backend/API_DOCUMENTATION.md` - API endpoint dokümantasyonu
- `backend/README.md` - Backend detaylı dokümantasyonu
- Kod içi dokümantasyon: Tüm modüller detaylı docstring'ler içerir

## 🐛 Sorun Giderme

### Snyk CLI Bulunamadı

Snyk CLI'nin yolunu `metric_runner.py` dosyasında güncelleyin:

```python
SNYK_PATH = r"C:\Users\YOUR_USERNAME\AppData\Roaming\npm\snyk.cmd"  # Windows
# veya
SNYK_PATH = "/usr/local/bin/snyk"  # Linux/Mac
```

### DeepSource API Hatası

- API token'ın geçerli olduğundan emin olun
- Repository bilgilerinin doğru olduğunu kontrol edin
- Network bağlantınızı kontrol edin

### Encoding Hatası (Windows)

Windows'ta emoji karakterleri sorun çıkarabilir. Kod içindeki emoji'ler kaldırılmıştır.

## 📄 Lisans

Bu proje eğitim/araştırma amaçlıdır.


1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add some amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın


---

**Not**: Bu proje, AI kod analiz araçlarını karşılaştırmak için geliştirilmiştir. Tüm kodlar detaylı açıklamalar içerir.
