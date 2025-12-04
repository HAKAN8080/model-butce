# Model Bütçe - Hızlı Başlangıç

## 📦 Kurulum

### 1. Dosyayı İndir ve Aç
```bash
# İndirdiğiniz model-butce.tar.gz dosyasını açın
tar -xzf model-butce.tar.gz
cd model-butce
```

### 2. Python Paketlerini Yükle
```bash
pip install -r requirements.txt
```

Gerekli paketler:
- streamlit==1.29.0
- pandas==2.1.4
- plotly==5.18.0
- numpy==1.26.2
- openpyxl==3.1.2

### 3. Uygulamayı Başlat
```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak açılacak: `http://localhost:8501`

## 📁 Proje Yapısı

```
model-butce/
├── app.py                      # Ana uygulama
├── requirements.txt            # Gerekli paketler
├── README.md                   # Proje açıklaması
├── KULLANIM_KILAVUZU.md       # Detaylı kullanım kılavuzu
├── data/                       # Örnek veri dosyaları
│   ├── sample_products.csv    # 129 ürün
│   ├── sample_stores.csv      # 39 mağaza
│   └── sample_sales.csv       # 52 haftalık satış
├── modules/                    # Ana modüller
│   ├── carpan.py              # Çarpan modülü
│   ├── clustering.py          # KTG/STG modülü
│   └── model_butce.py         # Model bütçe modülü
├── utils/                      # Yardımcı fonksiyonlar
│   ├── data_loader.py         # Veri yükleme
│   └── calculations.py        # Hesaplamalar
└── saved_data/                 # Kayıtlar
    ├── carpan_sets/           # Çarpan setleri
    └── ktg_stg/               # STG konfigürasyonları
```

## 🚀 İlk Kullanım

### Adım 1: Çarpan Oluştur
1. Sol menüden "📊 Çarpan Modülü" seç
2. Sezon gir: `26SS`
3. Hiyerarşi seç (örn: Aksesuar > Koku > Oda Kokusu)
4. Grafikte çarpanları düzenle
5. İsim ver ve kaydet

### Adım 2: STG Hesapla
1. "🎯 Clustering" modülüne geç
2. "STG - Satış Trend Grup" tab'ına tıkla
3. Hiyerarşi seç (Aksesuar > Koku > Oda Kokusu)
4. "STG Hesapla" butonuna bas
5. "STG Kaydet" ile kaydet

### Adım 3: Sipariş Hesapla
1. "💼 Model Bütçe" modülüne geç
2. Bir ürün seç
3. Çarpan setini seç
4. KTG'leri seç (örn: Normal-Orta, Büyük-Hızlı)
5. STG referans KTG seç
6. Haftalık hedef gir (örn: 10)
7. Ürün ömrünü belirle (örn: 1-52)
8. "Sipariş İhtiyacını Hesapla" butonuna bas

## 📊 Örnek Veri

Proje içinde örnek veriler hazır:
- **129 ürün** (Aksesuar, Ev Tekstili, Dekorasyon)
- **39 mağaza** (9 KTG grubunda)
- **52 haftalık** satış geçmişi

## 🔧 Sorun Giderme

**Port zaten kullanımda hatası:**
```bash
streamlit run app.py --server.port 8502
```

**Modül import hatası:**
Ana dizinden (`model-butce/`) çalıştırdığınızdan emin olun.

**Veri yüklenmiyor:**
`data/` klasörünün doğru yerde olduğunu kontrol edin.

## 📖 Daha Fazla Bilgi

Detaylı kullanım için `KULLANIM_KILAVUZU.md` dosyasını okuyun.

## 🎯 Önemli Notlar

1. Bu prototip 3 modülün basit versiyonunu içerir
2. Gerçek datanızı yüklemek için CSV formatını koruyun
3. 8000 SKU için performans optimizasyonu gerekebilir
4. Modüller birbirinden bağımsız çalışır, sırayla kullanın

## 🌟 Özellikler

✅ İnteraktif Plotly grafikleri
✅ Haftalık çarpan düzenleme
✅ KTG ve STG yönetimi
✅ Otomatik sipariş hesaplama
✅ JSON formatında kayıt sistemi
✅ Türkçe arayüz ve doküman

---

**İyi Çalışmalar!** 🚀
