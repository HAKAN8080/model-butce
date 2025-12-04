# Model Bütçe - Kullanım Kılavuzu

## 🚀 Kurulum ve Başlangıç

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatma
```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresinde açılacaktır.

---

## 📊 Modül 1: Çarpan Modülü

### Amaç
Geçmiş satış verilerine dayalı haftalık çarpan değerlerini belirlemek ve kaydetmek.

### Kullanım Adımları

1. **Sezon Girişi**
   - Soldaki menüden sezon kodunu girin (örn: `26SS`, `26FW`)

2. **Veri Kaynağı Seçimi**
   - **Hiyerarşi:** Ana Grup > Üst Grup > Alt Grup seçerek hiyerarşi bazlı çarpan oluşturun
   - **Model/SKU:** Belirli bir model veya SKU için çarpan oluşturun

3. **Grafik Düzenleme**
   - Sol tarafta 52 haftalık satış grafiği görünür (0-100 skala)
   - Sağ taraftan hafta seçip slider ile değer değiştirebilirsiniz
   - Grafiği görmek için hiyerarşi veya model seçmelisiniz

4. **Toplu İşlemler**
   - Başlangıç-Bitiş haftası belirleyip toplu çarpan uygulayabilirsiniz
   - Örnek: Hafta 10-20 arası +30% artış

5. **Kaydetme**
   - Çarpan set adı girin
   - "Kaydet" butonuna basın
   - Kaydedilen setler dropdown'dan yüklenebilir

### Önemli Notlar
- Normalize edilen grafik 0-100 arası gösterilir
- Her hafta için ayrı çarpan değeri belirlenir
- Yeni ürünler için varsayılan olarak hiyerarşi grafiği gelir

---

## 🎯 Modül 2: Clustering

### Amaç
Mağazaları kapasiteye göre gruplamak (KTG) ve satış trend katsayılarını hesaplamak (STG).

### KTG - Kapasite Trend Grup

**9 Grup:**
- Büyük-Hızlı, Büyük-Orta, Büyük-Yavaş
- Normal-Hızlı, Normal-Orta, Normal-Yavaş
- Küçük-Hızlı, Küçük-Orta, Küçük-Yavaş

**Kullanım:**
1. KTG dağılımını ve mağaza sayılarını görüntüleyin
2. Her KTG'deki mağazaları listeleyin
3. Bu gruplar Model Bütçe'de kullanılır

### STG - Satış Trend Grup

**Amaç:** Hiyerarşi bazında her KTG için ortalama haftalık satış hesaplamak.

**Kullanım Adımları:**
1. Ana Grup > Üst Grup > Alt Grup seçin
2. "STG Hesapla" butonuna basın
3. Her KTG için ortalama haftalık satış görüntülenir
4. "STG Kaydet" ile kaydedin
5. Kaydedilen STG'ler Model Bütçe'de kullanılır

**Örnek:**
```
Koku > Oda Kokusu için STG:
- Normal-Orta: 8 adet/hafta
- Büyük-Hızlı: 15 adet/hafta
- Küçük-Yavaş: 3 adet/hafta
```

---

## 💼 Modül 3: Model Bütçe

### Amaç
Ürünler için sipariş ihtiyacını hesaplamak.

### Kullanım Adımları

#### 1. Ürün Filtreleme
- Soldaki menüden Ana Grup, Üst Grup ve Ürün Tipi filtrelerini kullanın
- Ürün listesinden bir ürün seçin

#### 2. Hesaplama Parametreleri

**a. Sezon ve Çarpan:**
- Sezon kodunu girin
- Kaydedilmiş çarpan setlerinden birini seçin

**b. KTG Seçimi:**
- Ürünün gideceği KTG gruplarını seçin
- Örnek: Normal-Orta, Büyük-Hızlı

**c. STG ve Referans KTG:**
- Ürün hiyerarşisine uygun STG otomatik seçilir
- Referans KTG seçin (örn: Normal-Orta)
- Bu gruptaki ortalama satış gösterilir

**d. Haftalık Hedef:**
- Referans KTG'deki bir mağazanın haftalık hedefini girin
- Örnek: 10 adet/hafta

**e. Ürün Ömrü:**
- Başlangıç haftası (1-52)
- Bitiş haftası (1-52)

#### 3. Hesaplama
- "Sipariş İhtiyacını Hesapla" butonuna basın
- Sonuçlar görüntülenir

### Hesaplama Mantığı

```
Her KTG için:
  - Mağaza sayısı × Haftalık hedef × STG katsayısı × Çarpan (her hafta)

Toplam = Tüm KTG'lerin toplamı × Ürün ömrü hafta sayısı
```

**Örnek Hesaplama:**

Parametreler:
- Seçili KTG: Normal-Orta (4 mağaza)
- Referans KTG: Normal-Orta (ort. 8 adet/hafta)
- Haftalık hedef: 10 adet
- STG katsayısı: 1.0 (kendi grubumuz)
- Çarpan: Hafta 1-10 arası ortalama 0.8
- Ürün ömrü: 10 hafta

Hesaplama:
```
Normal-Orta için:
4 mağaza × 10 hedef × 1.0 STG × (hafta1_çarpan + hafta2_çarpan + ... hafta10_çarpan)
```

### Sonuç Ekranı

**Gösterilenler:**
- Toplam sipariş ihtiyacı (adet)
- KTG bazında dağılım tablosu
- Her KTG için:
  - Mağaza sayısı
  - STG katsayısı
  - Sipariş miktarı
- Özet metrikler

---

## 📁 Veri Yapısı

### Örnek Veriler

**Ürünler:** `data/sample_products.csv`
- 129 SKU
- Hiyerarşi: Ana Grup > Üst Grup > Alt Grup
- Ürün tipleri: Carryover, NOS, Yeni
- Brüt marj bilgisi

**Mağazalar:** `data/sample_stores.csv`
- 39 mağaza
- 9 KTG grubuna dağıtılmış
- M² bilgisi

**Satışlar:** `data/sample_sales.csv`
- 52 haftalık geçmiş
- SKU × Mağaza × Hafta bazında

### Kaydedilen Veriler

**Çarpan Setleri:** `saved_data/carpan_sets/`
- JSON formatında
- Sezon_İsim.json şeklinde

**STG Konfigürasyonu:** `saved_data/ktg_stg/`
- config.json içinde
- Hiyerarşi bazlı STG katsayıları

---

## 🔧 İpuçları

### Yeni Ürünler için Çarpan
1. Önce hiyerarşi çarpanını oluşturun
2. İsterseniz benzer ürün çarpanını kullanabilirsiniz

### STG Hesaplama
- Her hiyerarşi için ayrı STG hesaplayın
- Yeterli satış datası olan hiyerarşileri seçin

### Model Bütçe Hesaplama
- Önce Çarpan ve STG'yi hazırlayın
- Birden fazla KTG seçerek geniş dağıtım yapabilirsiniz
- Farklı sezonlar için ayrı çarpan setleri oluşturun

---

## ❓ Sık Sorulan Sorular

**S: Çarpan grafiği boş görünüyor?**
C: Önce hiyerarşi veya model seçmelisiniz. Seçtiğiniz veri için satış geçmişi yoksa grafik boş olabilir.

**S: STG hesaplanamıyor?**
C: Seçtiğiniz hiyerarşi için yeterli satış datası olmayabilir. Daha üst seviye hiyerarşi deneyin.

**S: Model Bütçe'de çarpan yok diyor?**
C: Önce Çarpan Modülü'nde sezon için çarpan oluşturup kaydetmelisiniz.

**S: Hesaplanan sipariş çok düşük/yüksek?**
C: Haftalık hedefi, seçili KTG'leri ve ürün ömrünü kontrol edin. Çarpan değerleri de sonucu etkiler.

---

## 🎯 İş Akışı Özeti

```
1. ÇARPAN MODÜLÜ
   ↓
   - Sezon belirle (26SS)
   - Hiyerarşi veya Model seç
   - 52 haftalık çarpanları düzenle
   - Çarpan setini kaydet
   ↓
2. CLUSTERING MODÜLÜ
   ↓
   - Hiyerarşi seç (Ana > Üst > Alt)
   - STG hesapla
   - STG'yi kaydet
   ↓
3. MODEL BÜTÇE MODÜLÜ
   ↓
   - Ürün seç
   - Çarpan seti yükle
   - KTG'leri seç
   - STG ve referans KTG seç
   - Haftalık hedef gir
   - Ürün ömrünü belirle
   - Hesapla!
   ↓
   SİPARİŞ İHTİYACI HAZIR ✅
```

---

## 🐛 Sorun Giderme

**Hata: Veri dosyaları yüklenemedi**
- `data/` klasörünün mevcut olduğundan emin olun
- CSV dosyalarının UTF-8-SIG encoding olduğunu kontrol edin

**Hata: Modül import edilemiyor**
- Ana dizinden `streamlit run app.py` çalıştırın
- `modules/` ve `utils/` klasörlerinin mevcut olduğunu kontrol edin

**Performans sorunları**
- Gerçek datada 8000 SKU olduğunda filtreleme kullanın
- Büyük veri setleri için önbellek mekanizması eklenebilir

---

## 📞 Destek

Thorius AR4U Platform
Retail Analytics & Planning

Sorularınız için proje yöneticinizle iletişime geçin.
