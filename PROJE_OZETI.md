# Model Bütçe Projesi - Teknik Özet

## 🎯 Proje Amacı

Retail operasyonları için ürünlerin sipariş ihtiyacını belirlemeye yönelik kapsamlı bir planlama platformu.

## 📊 Sistem Mimarisi

### Veri Akışı
```
Geçmiş Satış Datası
    ↓
Çarpan Modülü → 52 haftalık çarpan setleri
    ↓
Clustering Modülü → KTG grupları + STG katsayıları
    ↓
Model Bütçe Modülü → Sipariş ihtiyacı hesaplama
    ↓
Sonuç: Toplam Sipariş + KTG Dağılımı
```

## 🔧 Teknik Stack

- **Frontend:** Streamlit 1.29.0
- **Grafikler:** Plotly 5.18.0
- **Veri İşleme:** Pandas 2.1.4, Numpy 1.26.2
- **Dosya İşleme:** Openpyxl 3.1.2
- **Kayıt:** JSON format

## 📁 Modül Detayları

### 1. Çarpan Modülü (`modules/carpan.py`)

**Amaç:** Haftalık satış çarpanlarını belirleme ve kaydetme

**Özellikler:**
- Hiyerarşi veya Model/SKU bazlı veri seçimi
- Plotly ile interaktif grafik
- 52 haftalık çarpan düzenleme (slider + toplu işlem)
- Sezon bazlı kayıt (JSON)
- 0-100 skala normalizasyon

**Kayıt Formatı:**
```json
{
  "name": "Çarpan_26SS",
  "sezon": "26SS",
  "hierarchy": {
    "type": "hiyerarşi",
    "ana_grup": "Aksesuar",
    "ust_grup": "Koku",
    "alt_grup": "Oda Kokusu"
  },
  "carpan_values": [52 adet haftalık değer]
}
```

### 2. Clustering Modülü (`modules/clustering.py`)

**Amaç:** Mağaza gruplandırma (KTG) ve satış trend katsayıları (STG)

**KTG (Kapasite Trend Grup):**
- 9 grup: Büyük/Normal/Küçük × Hızlı/Orta/Yavaş
- Mağazalar m² ve satış hızına göre gruplandırılmış
- Sabit yapı, tüm ürünler için aynı

**STG (Satış Trend Grup):**
- Hiyerarşi bazlı hesaplama
- Her KTG için ortalama haftalık satış
- Referans grup karşılaştırması için katsayılar

**STG Hesaplama Algoritması:**
```python
# Hiyerarşideki ürünleri bul
filtered_products = products[hierarchy_filter]

# Bu ürünlerin satışlarını getir
sales_data = sales[sales.SKU.isin(filtered_products)]

# Mağaza KTG'lerini birleştir
merged = sales_data.merge(stores[['Magaza_Kodu', 'KTG']])

# KTG bazında ortalama haftalık satış
ktg_averages = merged.groupby('KTG')['Satis_Adet'].mean()
```

### 3. Model Bütçe Modülü (`modules/model_butce.py`)

**Amaç:** Sipariş ihtiyacı hesaplama

**Hesaplama Formülü:**
```python
for each KTG in selected_KTGs:
    magaza_sayisi = count(stores[KTG])
    stg_katsayisi = ktg_avg / reference_ktg_avg
    
    for each week in urun_omru:
        carpan = carpan_values[week] / 100
        haftalik_siparis = (magaza_sayisi × haftalik_hedef × 
                           stg_katsayisi × carpan)
    
    total += sum(haftalik_siparis)
```

**Input Parametreleri:**
- Sezon ve Çarpan Seti
- KTG Seçimi (multi-select)
- STG Referans Grup
- Haftalık Hedef (referans grup için)
- Ürün Ömrü (başlangıç-bitiş haftası)

**Output:**
- Toplam sipariş ihtiyacı
- KTG bazında dağılım
- Her KTG için: mağaza sayısı, STG katsayısı, sipariş miktarı

## 📊 Veri Yapıları

### Ürün Master (`data/sample_products.csv`)
```csv
SKU,Model_Kodu,Ana_Grup,Ust_Grup,Alt_Grup,Urun_Tipi,Brut_Marj_%,Urun_Adi
SKU10000,MDL10000,Aksesuar,Koku,Oda Kokusu,Carryover,56.19,Oda Kokusu A
```

### Mağaza Master (`data/sample_stores.csv`)
```csv
Magaza_Kodu,Magaza_Adi,Sehir,KTG,Buyukluk,Hiz,M2
M1001,Mağaza 1001,İstanbul,Büyük-Hızlı,Büyük,Hızlı,1200
```

### Satış Datası (`data/sample_sales.csv`)
```csv
SKU,Magaza_Kodu,Hafta,Satis_Adet
SKU10000,M1001,2024-W01,5
```

## 🔄 İş Akışı

### Başlangıç Durumu
```
data/
├── sample_products.csv    (129 ürün)
├── sample_stores.csv      (39 mağaza)
└── sample_sales.csv       (1000 satış kaydı)
```

### Kullanıcı Etkileşimi
```
1. Çarpan Oluşturma:
   User → Hiyerarşi seç → Grafik düzenle → Kaydet
   Result: saved_data/carpan_sets/26SS_Carpan1.json

2. STG Hesaplama:
   User → Hiyerarşi seç → Hesapla → Kaydet
   Result: saved_data/ktg_stg/config.json (STG bölümü)

3. Sipariş Hesaplama:
   User → Ürün + Çarpan + KTG + STG + Hedef + Ömür → Hesapla
   Result: Ekranda sonuç gösterimi
```

## 🎨 UI Tasarımı

### Ana Sayfa
- Modül kartları
- Sistem durumu metrikleri
- Hızlı başlangıç rehberi

### Çarpan Modülü
- Sol: Ayarlar (sezon, hiyerarşi/model seçimi)
- Orta: 52 haftalık grafik (Plotly line chart)
- Sağ: Düzenleme paneli (hafta seç, slider, toplu işlem)
- Alt: Kaydetme bölümü

### Clustering Modülü
- Tab 1: KTG (mağaza dağılımı, detay listesi)
- Tab 2: STG (hiyerarşi seç, hesapla, kayıtları görüntüle)

### Model Bütçe Modülü
- Sol sidebar: Filtreler (hiyerarşi, ürün tipi)
- Üst: Ürün seçimi ve bilgileri
- Orta: Hesaplama parametreleri (4 bölüm)
- Alt: Hesapla butonu ve sonuçlar

## 🚀 Performans Notları

### Mevcut Durum (Prototip)
- 129 ürün
- 39 mağaza
- 1000 satış kaydı
- Yanıt süresi: <1 saniye

### Gerçek Senaryoda (8000 SKU)
**Optimizasyon önerileri:**
1. Pandas query optimizasyonu
2. Veri önbellekleme (@st.cache_data)
3. Lazy loading (sayfalama)
4. Veritabanı kullanımı (SQLite/PostgreSQL)
5. Async veri yükleme

## 🔐 Veri Güvenliği

- Veriler local'de saklanır
- JSON formatında şifreleme eklenebilir
- Kullanıcı yetkilendirme sistemi eklenebilir
- Audit log sistemi eklenebilir

## 📈 Gelecek Geliştirmeler

### Öncelik 1 (Temel)
- [ ] Gerçek veri entegrasyonu
- [ ] Excel upload/download
- [ ] Çoklu sezon karşılaştırma
- [ ] Raporlama modülü

### Öncelik 2 (İleri)
- [ ] Modül 4: Termin/Alım Planlama
- [ ] Modül 5: Asortileme-Paketleme
- [ ] Dashboard ve analytics
- [ ] Email notifications
- [ ] API entegrasyonu

### Öncelik 3 (Optimizasyon)
- [ ] Machine learning ile çarpan tahmini
- [ ] Otomatik anomali tespiti
- [ ] What-if senaryoları
- [ ] Multi-user collaboration

## 🐛 Bilinen Limitasyonlar

1. **Veri Boyutu:** Şu an küçük veri seti ile test edildi
2. **Performans:** 8000 SKU için test edilmedi
3. **Eşzamanlılık:** Multi-user desteği yok
4. **Versiyonlama:** Değişiklik geçmişi takibi yok
5. **Yedekleme:** Otomatik backup yok

## 📞 Teknik Destek

### Geliştirme Ortamı
```bash
Python 3.12
Streamlit 1.29.0
Ubuntu 24
```

### Debug Modu
```bash
streamlit run app.py --logger.level=debug
```

### Loglar
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Lisans ve Kullanım

Thorius AR4U Platform - Retail Analytics
© 2024 - Tüm hakları saklıdır

---

**Proje Durumu:** ✅ Prototip Tamamlandı
**Son Güncelleme:** Aralık 2024
**Versiyon:** 1.0.0
