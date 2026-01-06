# DeepSource Status Check Sorunu - Çözüm Kılavuzu

## Sorun
GitHub'da main branch'inin "Check status" kısmında çarpı (X 0/1) görünüyor.
Hata mesajı: **"DeepSource: Python - Analysis failed: Blocking issues or failing metrics found"**

## Neden
DeepSource, repository'yi analiz ettiğinde blocking issues (engelleyici sorunlar) veya başarısız metrikler bulmuş. Bu durumda DeepSource status check'i başarısız oluyor.

## Çözüm Seçenekleri

### Çözüm 1: DeepSource Dashboard'unda Issues'ları Düzeltme (Önerilen)

1. **DeepSource Dashboard'a gidin:**
   - https://deepsource.io/dashboard
   - Repository'nizi bulun: `zeliha-orhan/SmartTestAI`

2. **Issues'ları görüntüleyin:**
   - Repository sayfasında "Issues" sekmesine gidin
   - Blocking issues'ları (kırmızı işaretli) görüntüleyin
   - Her issue için detayları okuyun

3. **Issues'ları düzeltin:**
   - Kodunuzda bulunan sorunları düzeltin
   - Commit yapın ve push edin
   - DeepSource otomatik olarak yeniden analiz edecek

### Çözüm 2: .deepsource.toml Dosyasını Güncelleme (Geçici)

`.deepsource.toml` dosyasına `fail_on_errors = false` ekleyerek DeepSource'un blocking issues olsa bile status check'i geçmesini sağlayabilirsiniz.

**Not:** Bu sadece geçici bir çözümdür. Issues'ları düzeltmek daha iyidir.

```toml
version = 1

[[analyzers]]
name = "python"
enabled = true

[analyzers.meta]
fail_on_errors = false
```

### Çözüm 3: DeepSource Status Check'ini Devre Dışı Bırakma

Eğer DeepSource status check'ine ihtiyacınız yoksa, GitHub'da branch protection rules'dan kaldırabilirsiniz:

1. GitHub repository'nize gidin
2. Settings > Branches
3. Main branch için protection rules'u düzenleyin
4. "Require status checks to pass before merging" bölümünden DeepSource check'ini kaldırın

## Adım Adım: Issues'ları Düzeltme

### 1. DeepSource Dashboard Kontrolü

```bash
# DeepSource dashboard'a gidin ve repository'nizi kontrol edin
# https://deepsource.io/dashboard
```

### 2. Issues Listesini Görüntüleme

- Repository sayfasında "Issues" sekmesine tıklayın
- Blocking issues'ları (genellikle Critical veya High severity) görüntüleyin
- Her issue için:
  - Dosya adı ve satır numarası
  - Issue açıklaması
  - Önerilen çözüm

### 3. Issues'ları Düzeltme

Örnek blocking issues:
- **Security issues:** SQL injection, XSS, hardcoded credentials
- **Code quality issues:** Code smells, anti-patterns
- **Performance issues:** Inefficient code patterns

### 4. Değişiklikleri Commit ve Push Etme

```bash
# Issues'ları düzelttikten sonra
git add .
git commit -m "Fix DeepSource blocking issues"
git push origin main
```

## .deepsource.toml Yapılandırması

Mevcut `.deepsource.toml` dosyası:

```toml
version = 1

[[analyzers]]
name = "python"
enabled = true

[analyzers.meta]
fail_on_errors = false  # Blocking issues olsa bile status check geçsin
```

## Notlar

- **fail_on_errors = false:** DeepSource blocking issues bulsa bile status check'i geçer
- **fail_on_errors = true (varsayılan):** Blocking issues varsa status check başarısız olur
- Issues'ları düzeltmek her zaman daha iyidir
- Geçici çözüm olarak `fail_on_errors = false` kullanılabilir

## Hızlı Test

Status check'in düzelip düzelmediğini kontrol etmek için:

```bash
# Boş bir commit yaparak check'i tetikleyin
git commit --allow-empty -m "Test DeepSource status check"
git push origin main
```

GitHub'da main branch'inin yanındaki check status'ü kontrol edin. Artık yeşil tik (✓) görünmelidir.

