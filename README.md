# Model Bütçe - Retail Sipariş İhtiyaç Belirleme Sistemi

Retail operasyonları için sipariş ihtiyacını belirlemeye yönelik kapsamlı bir planlama platformu.

## Modüller

### 1. Çarpan Modülü
Geçmiş satış verilerine dayalı haftalık çarpan belirleme modülü.
- Haftalık satış grafiği (52 hafta)
- İnteraktif çarpan düzenleme
- Sezon bazlı kayıt sistemi

### 2. Clustering Modülü
Mağaza gruplandırma ve satış trend analizi.
- **KTG (Kapasite Trend Grup):** 9 grup (Büyük/Normal/Küçük × Hızlı/Orta/Yavaş)
- **STG (Satış Trend Grup):** Hiyerarşi bazlı satış hız katsayıları

### 3. Model Bütçe Modülü
Ana sipariş ihtiyacı hesaplama modülü.
- Ürün listesi ve filtreleme
- KTG seçimi
- STG bazlı hesaplama
- Ürün ömrü belirleme
- Toplam sipariş ihtiyacı

## Kurulum

```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
streamlit run app.py
```

## Veri Yapısı

### Ürün Tipleri
- **Carryover:** Mevsimsel/dönemsel devam eden ürünler
- **NOS (Never Out of Stock):** Hiç tükenmemesi gereken ürünler
- **Yeni Ürün:** Yeni lansmanlar

### Hiyerarşi
3 seviye: Ana Grup → Üst Grup → Alt Grup

## Hesaplama Formülü

```
Toplam Sipariş = Σ (Mağaza Sayısı_KTG × Haftalık Hedef × STG_Katsayısı × Çarpan_Haftalık × Ürün Ömrü)
```

## Teknoloji

- Python 3.8+
- Streamlit
- Plotly (İnteraktif grafikler)
- Pandas (Veri işleme)

## Geliştirici

Thorius AR4U Platform - Retail Analytics
