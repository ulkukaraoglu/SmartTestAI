# Metrik Hesaplama Fonksiyonları Dokümantasyonu

## 📊 İncelenecek Parametreler ve Metrikler

Proje kapsamında araçların yetkinliklerini ölçmek için çok boyutlu bir değerlendirme matrisi kullanılmaktadır.

### 1. Hata Tespit Başarısı (Defect Detection Accuracy)

**Açıklama:** Araçların mevcut hataları tespit etme oranı; precision ve recall metrikleri kullanılarak hesaplanır.

**Hesaplama:**
- **Precision (Doğruluk):** `TP / (TP + FP)`
  - Doğru pozitif / (Doğru pozitif + Yanlış pozitif)
  - Bulunan issue'ların ne kadarının gerçekten hata olduğunu gösterir
  
- **Recall (Geri Çağırma):** `TP / (TP + FN)`
  - Doğru pozitif / (Doğru pozitif + Yanlış negatif)
  - Gerçek hataların ne kadarının bulunduğunu gösterir
  
- **F1 Score:** `2 * (precision * recall) / (precision + recall)`
  - Precision ve recall'un harmonik ortalaması
  - Dengeli bir performans ölçüsü

**Kullanım:**
```python
from metrics.advanced_metrics import AdvancedMetricsCalculator

calculator = AdvancedMetricsCalculator()
accuracy = calculator.calculate_defect_detection_accuracy(
    detected_issues=detected_issues,  # Araç tarafından bulunan issue'lar
    ground_truth=ground_truth         # Gerçekte var olan issue'lar
)

print(f"Precision: {accuracy['precision']:.2%}")
print(f"Recall: {accuracy['recall']:.2%}")
print(f"F1 Score: {accuracy['f1_score']:.2%}")
```

---

### 2. Kod Kapsama Oranı (Code Coverage)

**Açıklama:** Yapay zeka tarafından oluşturulan test senaryolarının hedef yazılımın mantıksal yollarını ve kod satırlarını ne ölçüde kapsadığı.

**Hesaplama:**
- **Code Coverage:** `(Analiz edilen satırlar / Toplam satırlar) * 100`
- **Files Analyzed:** Analiz edilen dosya sayısı
- **Lines Analyzed:** Analiz edilen satır sayısı

**Kullanım:**
```python
coverage = calculator.calculate_code_coverage(
    raw_data=raw_data,      # Araçtan gelen ham veri
    total_lines=1000,       # Toplam kod satırı sayısı
    total_files=50          # Toplam dosya sayısı
)

print(f"Code Coverage: {coverage['code_coverage']:.2f}%")
print(f"Files Analyzed: {coverage['files_analyzed']}")
```

---

### 3. Kod Kalitesi ve Standart Uyumu

**Açıklama:** Oluşturulan test kodlarının ve düzeltme önerilerinin okunabilirlik, bakım yapılabilirlik ve endüstri standartlarına (örn. Clean Code prensipleri) uygunluğu analiz edilir.

**Not:** Bu metrik genellikle manuel değerlendirme veya ek analiz araçları gerektirir.

**Değerlendirme Kriterleri:**
- Kod okunabilirliği
- Bakım yapılabilirlik
- Clean Code prensipleri uyumu
- Endüstri standartlarına uygunluk

---

### 4. Yanlış Alarm Eğilimi (False Positive Rate)

**Açıklama:** Araçların hatasız kod bloklarını yanlışlıkla hatalı olarak raporlama sıklığı.

**Hesaplama:**
- **False Positive Rate:** `FP / (FP + TN)` veya `FP / Total Detected`
  - Yanlış pozitif / (Yanlış pozitif + Doğru negatif)
  - Bulunan issue'ların ne kadarının yanlış alarm olduğunu gösterir

**Kullanım:**
```python
accuracy = calculator.calculate_defect_detection_accuracy(
    detected_issues=detected_issues,
    ground_truth=ground_truth
)

print(f"False Positive Rate: {accuracy['false_positive_rate']:.2%}")
print(f"False Positives: {accuracy['false_positives']}")
```

---

### 5. Operasyonel Verimlilik

**Açıklama:** Aracın analiz ve çıktı üretme sürecini "Ortalama Çalışma Süresi" ve kaynak kullanımı (CPU/Bellek) üzerinden nicelleştirir.

**Hesaplama:**
- **Average Scan Time:** Ortalama tarama süresi (saniye)
- **CPU Usage Percent:** CPU kullanım yüzdesi
- **Memory Usage MB:** Bellek kullanımı (MB)

**Kullanım:**
```python
efficiency = calculator.calculate_operational_efficiency()

print(f"Average Scan Time: {efficiency['average_scan_time']:.2f}s")
print(f"CPU Usage: {efficiency['cpu_usage_percent']:.2f}%")
print(f"Memory Usage: {efficiency['memory_usage_mb']:.2f} MB")
```

---

## 🔧 Tüm Metrikleri Hesaplama

```python
from metrics.advanced_metrics import AdvancedMetricsCalculator

calculator = AdvancedMetricsCalculator()

# Tüm metrikleri hesapla
result = calculator.calculate_all_advanced_metrics(
    raw_data=raw_data,              # Araçtan gelen ham veri
    detected_issues=detected_issues, # Bulunan issue'lar
    ground_truth=ground_truth,      # Gerçek issue'lar (opsiyonel)
    scan_duration=12.5,              # Tarama süresi
    total_lines=1000,                # Toplam satır sayısı
    total_files=50                   # Toplam dosya sayısı
)

# Sonuçları kullan
print(f"Precision: {result.precision:.2%}")
print(f"Recall: {result.recall:.2%}")
print(f"F1 Score: {result.f1_score:.2%}")
print(f"Code Coverage: {result.code_coverage:.2f}%")
print(f"False Positive Rate: {result.false_positive_rate:.2%}")
print(f"Average Scan Time: {result.average_scan_time:.2f}s")
```

---

## 📝 Ground Truth Verisi

**Önemli:** Precision ve Recall hesaplamak için "ground truth" (gerçek hata listesi) gereklidir.

### Ground Truth Formatı

```python
ground_truth = [
    {
        "file": "app.py",
        "line": 18,
        "type": "SQL_INJECTION",
        "severity": "high"
    },
    {
        "file": "app.py",
        "line": 32,
        "type": "COMMAND_INJECTION",
        "severity": "high"
    }
]
```

### Ground Truth Oluşturma

1. **Manuel Olarak:** Test projelerindeki bilinen hataları listeleyin
2. **Test Projelerinden:** `vulnerable_demo` gibi kasıtlı hata içeren projelerden
3. **Uzman Değerlendirmesi:** Kod incelemesi yaparak gerçek hataları belirleyin

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Snyk vs DeepSource Karşılaştırması

```python
# Her iki araç için metrikleri hesapla
snyk_metrics = calculator.calculate_all_advanced_metrics(
    raw_data=snyk_raw_data,
    detected_issues=snyk_issues,
    ground_truth=ground_truth,
    scan_duration=snyk_duration
)

deepsource_metrics = calculator.calculate_all_advanced_metrics(
    raw_data=deepsource_raw_data,
    detected_issues=deepsource_issues,
    ground_truth=ground_truth,
    scan_duration=deepsource_duration
)

# Karşılaştır
print(f"Snyk Precision: {snyk_metrics.precision:.2%}")
print(f"DeepSource Precision: {deepsource_metrics.precision:.2%}")
```

### Senaryo 2: Benchmark Raporu Oluşturma

```python
# Tüm projeler için metrikleri topla
results = []
for project in ["flask_demo", "vulnerable_demo"]:
    metrics = calculate_metrics_for_project(project)
    results.append(metrics)

# Rapor oluştur
generate_benchmark_report(results)
```

---

## 📚 İlgili Dosyalar

- `backend/metrics/advanced_metrics.py` - Gelişmiş metrik hesaplama sınıfları
- `backend/metrics/base_metric.py` - Base metric sınıfı
- `backend/metrics/result_model.py` - Temel metrik modeli
- `backend/metrics/snyk_metrics.py` - Snyk metrik implementasyonu
- `backend/metrics/deepsource_metrics.py` - DeepSource metrik implementasyonu

