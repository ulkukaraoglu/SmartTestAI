# SmartTestAI Web UI

Modern ve kullanıcı dostu web arayüzü ile kod dosyalarınızı yükleyin ve Snyk Code ile DeepSource araçlarını kullanarak analiz edin.

## Özellikler

- 📁 **Dosya Yükleme**: Drag & drop veya tıklayarak dosya yükleme
- 🔍 **Çift Tarama**: Her iki araç (Snyk Code ve DeepSource) ile otomatik tarama
- 📊 **Detaylı Sonuçlar**: Karşılaştırmalı metrikler ve grafikler
- 🎯 **Gelişmiş Metrikler**: Precision, Recall, F1 Score analizi
- 💾 **Anında Görünüm**: Gerçek zamanlı tarama durumu ve sonuçlar

## Kurulum ve Kullanım

### Backend'i Başlatın (Web UI Otomatik Açılacak)

```bash
cd backend
pip install flask flask-cors
python app.py
```

Backend başlatıldığında:
- **Web UI otomatik olarak aynı port'tan servis edilir**: `http://localhost:5001`
- **API endpoint'leri**: `http://localhost:5001/api/*`

Tarayıcınızda **`http://localhost:5001`** adresini açarak Web UI'yi kullanmaya başlayabilirsiniz. Ayrı bir HTTP sunucusu çalıştırmanıza gerek yok!

## Kullanım

1. **Dosya Yükle**: Ana sayfada dosyalarınızı sürükleyip bırakın veya tıklayarak seçin
2. **Taramayı Başlat**: "🔍 Taramayı Başlat" butonuna tıklayın
3. **Sonuçları İncele**: Her iki araç için detaylı sonuçları görüntüleyin
4. **Detaylı Analiz**: "Detayları Göster" butonuna tıklayarak gelişmiş metrikleri görüntüleyin

## Desteklenen Dosya Formatları

- Python: `.py`
- JavaScript: `.js`
- Java: `.java`
- C/C++: `.cpp`, `.c`
- Go: `.go`
- Rust: `.rs`
- Text: `.txt`
- ZIP Arşivleri: `.zip`

## API Endpoint'leri

Web UI aşağıdaki backend endpoint'lerini kullanır:

- `POST /upload` - Dosya yükleme
- `POST /scan/code` - Snyk Code taraması
- `POST /scan/deepsource` - DeepSource taraması

## Sorun Giderme

### CORS Hatası

Eğer CORS hatası alıyorsanız:
1. Backend'de `flask-cors` paketinin yüklü olduğundan emin olun
2. Backend'in `http://localhost:5001` adresinde çalıştığından emin olun
3. Web UI'yi bir HTTP sunucusu üzerinden açın (basit dosya açma yerine)

### Backend Bağlantı Hatası

- Backend'in çalıştığını kontrol edin: `http://localhost:5001/projects`
- `app.js` dosyasındaki `API_BASE_URL` değerini kontrol edin

### Dosya Yükleme Hatası

- Dosya boyutunu kontrol edin (maksimum önerilen: 10MB)
- Desteklenen dosya formatlarını kontrol edin
- Backend loglarını kontrol edin

## Geliştirme

Web UI üç ana dosyadan oluşur:

- `index.html` - HTML yapısı
- `style.css` - Stil ve tasarım
- `app.js` - JavaScript işlevselliği

Değişiklik yapmak için bu dosyaları düzenleyebilirsiniz.
