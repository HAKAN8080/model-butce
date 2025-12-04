import pandas as pd
import numpy as np

def calculate_stg_coefficients(df_sales, df_products, df_stores, ana_grup, ust_grup, alt_grup):
    """
    Hiyerarşi için STG katsayılarını hesapla
    Her KTG için ortalama haftalık satış hesaplanır
    """
    
    # Hiyerarşideki ürünleri bul
    df_filtered = df_products[
        (df_products['Ana_Grup'] == ana_grup) &
        (df_products['Ust_Grup'] == ust_grup) &
        (df_products['Alt_Grup'] == alt_grup)
    ]
    
    filtered_skus = df_filtered['SKU'].unique()
    df_sales_filtered = df_sales[df_sales['SKU'].isin(filtered_skus)]
    
    # Mağaza KTG bilgilerini ekle
    df_merged = df_sales_filtered.merge(df_stores[['Magaza_Kodu', 'KTG']], on='Magaza_Kodu')
    
    # KTG bazında ortalama haftalık satış
    ktg_weekly_avg = df_merged.groupby('KTG')['Satis_Adet'].mean().to_dict()
    
    # Katsayıları hesapla (referans gruba göre)
    if not ktg_weekly_avg:
        return {}
    
    return ktg_weekly_avg

def calculate_order_need(
    selected_ktgs,
    df_stores,
    haftalik_hedef,
    stg_reference_ktg,
    stg_coefficients,
    carpan_values,
    urun_omru_baslangic,
    urun_omru_bitis
):
    """
    Sipariş ihtiyacını hesapla
    
    Formül: Toplam Sipariş = Σ (Mağaza Sayısı_KTG × Haftalık Hedef × STG_Katsayısı × Çarpan_Haftalık)
    """
    
    if not stg_coefficients or stg_reference_ktg not in stg_coefficients:
        return 0, {}
    
    reference_avg = stg_coefficients[stg_reference_ktg]
    
    toplam_siparis = 0
    ktg_detay = {}
    
    # Ürün ömrü haftaları (sadece index kullanıyoruz)
    hafta_indices = range(urun_omru_baslangic, urun_omru_bitis + 1)
    
    for ktg in selected_ktgs:
        # Bu KTG'deki mağaza sayısı
        magaza_sayisi = len(df_stores[df_stores['KTG'] == ktg])
        
        # STG katsayısı
        if ktg in stg_coefficients:
            ktg_avg = stg_coefficients[ktg]
            stg_katsayisi = ktg_avg / reference_avg
        else:
            stg_katsayisi = 1.0
        
        # Her hafta için hesaplama
        ktg_toplam = 0
        for hafta_idx in hafta_indices:
            if hafta_idx < len(carpan_values):
                carpan = carpan_values[hafta_idx] / 100  # 0-100 skaladan normale çevir
                haftalik_siparis = magaza_sayisi * haftalik_hedef * stg_katsayisi * carpan
                ktg_toplam += haftalik_siparis
        
        ktg_detay[ktg] = {
            'magaza_sayisi': magaza_sayisi,
            'stg_katsayisi': round(stg_katsayisi, 3),
            'toplam': round(ktg_toplam, 0)
        }
        
        toplam_siparis += ktg_toplam
    
    return round(toplam_siparis, 0), ktg_detay
