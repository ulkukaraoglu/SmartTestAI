# Comprehensive Vulnerability Test Project

Bu proje, tüm güvenlik açıklarını test etmek için tasarlanmış kapsamlı bir test projesidir.

## 📋 İçerdiği Güvenlik Açıkları

Bu proje aşağıdaki güvenlik açıklarını içerir:

### 1. **SQL Injection** (3 adet)
- `/user/<user_id>` - Line 35
- `/search?q=<query>` - Line 48
- `/user_by_email?email=<email>` - Line 62

### 2. **XSS (Cross-Site Scripting)** (3 adet)
- `/comment?text=<text>` - Line 75
- `/search_page?q=<query>` - Line 87
- `/profile?user=<username>` - Line 99

### 3. **Command Injection** (2 adet)
- `/ping?host=<host>` - Line 112
- `/execute?cmd=<command>` - Line 125

### 4. **Path Traversal** (2 adet)
- `/file?name=<filename>` - Line 138
- `/download?file=<filename>` - Line 150

### 5. **Hardcoded Credentials** (5 adet)
- Database password - Line 18
- API key - Line 19
- Secret key - Line 20
- Admin credentials - Line 21-22
- API endpoint - Line 175
- Database connection - Line 188

### 6. **Weak Hashing** (1 adet)
- `/login` - MD5 kullanımı - Line 163

### 7. **Insecure Deserialization** (1 adet)
- `/deserialize?data=<pickle>` - Line 201

### 8. **SSRF (Server-Side Request Forgery)** (1 adet)
- `/fetch?url=<url>` - Line 214

### 9. **Insecure Random** (1 adet)
- `/random` - Line 228

### 10. **Information Disclosure** (2 adet)
- `/debug` - Line 242
- `/error` - Line 254

### 11. **IDOR (Insecure Direct Object Reference)** (1 adet)
- `/user_data/<user_id>` - Line 268

### 12. **CORS Misconfiguration** (1 adet)
- `/api/cors` - Line 283

### 13. **Weak Cryptography** (1 adet)
- `/encrypt?data=<data>` - XOR şifreleme - Line 297

### 14. **Debug Mode** (1 adet)
- Production'da debug mode açık - Line 310

## 🎯 Toplam Güvenlik Açığı Sayısı

**26 adet güvenlik açığı** içerir:
- Critical: 6 adet
- High: 12 adet
- Medium: 8 adet

## 🚀 Kullanım

### Kurulum

```bash
cd test_projects/vulnerable_comprehensive
pip install -r requirements.txt
```

### Çalıştırma

```bash
python app.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

### Test Endpoint'leri

Ana sayfada (`http://localhost:5000/`) tüm endpoint'lerin listesi görüntülenir.

## 📊 Ground Truth

Bu projenin ground truth verileri `test_projects/ground_truth.json` dosyasında `vulnerable_comprehensive` anahtarı altında bulunmaktadır.

## ⚠️ UYARI

Bu proje **sadece test amaçlı** oluşturulmuştur. Production ortamında **ASLA** kullanılmamalıdır!

## 🔍 Test Senaryoları

### SQL Injection Test
```bash
curl "http://localhost:5000/user/1' OR '1'='1"
curl "http://localhost:5000/search?q=' UNION SELECT * FROM users--"
```

### XSS Test
```bash
curl "http://localhost:5000/comment?text=<script>alert('XSS')</script>"
```

### Command Injection Test
```bash
curl "http://localhost:5000/ping?host=localhost; cat /etc/passwd"
```

### Path Traversal Test
```bash
curl "http://localhost:5000/file?name=../../../etc/passwd"
```

### SSRF Test
```bash
curl "http://localhost:5000/fetch?url=http://localhost:5000/debug"
```

## 📝 Notlar

- Tüm güvenlik açıkları kasıtlı olarak eklenmiştir
- Her açık için açıklayıcı yorumlar mevcuttur
- Ground truth verileri doğru metrik hesaplama için kullanılır

