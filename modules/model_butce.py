import streamlit as st
import pandas as pd
import json
from utils.data_loader import load_products, load_stores, load_sales
from utils.calculations import calculate_order_need
from modules.carpan import load_carpan_sets
from modules.clustering import load_ktg_stg_config

def model_butce_module():
    st.header("💼 Model Bütçe Modülü")
    st.markdown("Ürünler için sipariş ihtiyacını hesaplayın.")
    
    # Veri yükleme
    df_products = load_products()
    df_stores = load_stores()
    df_sales = load_sales()
    
    if df_products.empty:
        st.error("Ürün datası yüklenemedi!")
        return
    
    # Sidebar - Filtreler
    st.sidebar.subheader("🔍 Filtreler")
    
    # Hiyerarşi filtreleri
    ana_grup_filter = st.sidebar.multiselect(
        "Ana Grup",
        sorted(df_products['Ana_Grup'].unique())
    )
    
    if ana_grup_filter:
        df_filtered = df_products[df_products['Ana_Grup'].isin(ana_grup_filter)]
        ust_grup_filter = st.sidebar.multiselect(
            "Üst Grup",
            sorted(df_filtered['Ust_Grup'].unique())
        )
    else:
        df_filtered = df_products
        ust_grup_filter = []
    
    if ust_grup_filter:
        df_filtered = df_filtered[df_filtered['Ust_Grup'].isin(ust_grup_filter)]
    
    # Ürün tipi filtresi
    urun_tipi_filter = st.sidebar.multiselect(
        "Ürün Tipi",
        ['Carryover', 'NOS', 'Yeni']
    )
    
    if urun_tipi_filter:
        df_filtered = df_filtered[df_filtered['Urun_Tipi'].isin(urun_tipi_filter)]
    
    # Ürün listesi
    st.subheader(f"📦 Ürün Listesi ({len(df_filtered)} ürün)")
    
    # Ürün seçimi
    selected_sku = st.selectbox(
        "Ürün Seç",
        [""] + df_filtered['SKU'].tolist(),
        format_func=lambda x: f"{x} - {df_filtered[df_filtered['SKU']==x]['Urun_Adi'].values[0]}" if x and x in df_filtered['SKU'].values else x
    )
    
    if selected_sku:
        st.divider()
        
        # Seçili ürün bilgileri
        urun = df_filtered[df_filtered['SKU'] == selected_sku].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("SKU", urun['SKU'])
        with col2:
            st.metric("Model", urun['Model_Kodu'])
        with col3:
            st.metric("Ürün Tipi", urun['Urun_Tipi'])
        with col4:
            st.metric("Brüt Marj %", f"{urun['Brut_Marj_%']:.1f}%")
        
        st.markdown(f"**Hiyerarşi:** {urun['Ana_Grup']} > {urun['Ust_Grup']} > {urun['Alt_Grup']}")
        
        st.divider()
        
        # ===== HESAPLAMA PARAMETRELERİ =====
        st.subheader("⚙️ Hesaplama Parametreleri")
        
        # 1. Sezon ve Çarpan Seçimi
        col_param1, col_param2 = st.columns(2)
        
        with col_param1:
            sezon = st.text_input("Sezon", value="26SS")
            
            # Kaydedilmiş çarpan setlerini yükle
            carpan_sets = load_carpan_sets(sezon)
            
            if carpan_sets:
                carpan_names = [s['name'] for s in carpan_sets]
                selected_carpan = st.selectbox("Çarpan Seti", [""] + carpan_names)
                
                if selected_carpan:
                    carpan_data = next(s for s in carpan_sets if s['name'] == selected_carpan)
                    carpan_values = carpan_data['carpan_values']
                    st.success(f"✅ Çarpan yüklendi: {selected_carpan}")
                else:
                    carpan_values = None
                    st.warning("⚠️ Çarpan seti seçilmedi")
            else:
                st.warning("⚠️ Bu sezon için kaydedilmiş çarpan bulunamadı")
                carpan_values = None
        
        with col_param2:
            # 2. KTG Seçimi
            st.markdown("**KTG Seçimi** (Ürünün gideceği gruplar)")
            
            ktg_groups = ['Büyük-Hızlı', 'Büyük-Orta', 'Büyük-Yavaş',
                          'Normal-Hızlı', 'Normal-Orta', 'Normal-Yavaş',
                          'Küçük-Hızlı', 'Küçük-Orta', 'Küçük-Yavaş']
            
            selected_ktgs = st.multiselect(
                "KTG'ler",
                ktg_groups,
                default=['Normal-Orta']
            )
        
        # 3. STG ve Haftalık Hedef
        col_param3, col_param4 = st.columns(2)
        
        with col_param3:
            # STG yükle
            config = load_ktg_stg_config()
            
            if config and config.get('stg'):
                stg_keys = list(config['stg'].keys())
                
                # Bu ürünün hiyerarşisine uygun STG'yi bul
                urun_hierarchy_key = f"{urun['Ana_Grup']}_{urun['Ust_Grup']}_{urun['Alt_Grup']}"
                
                if urun_hierarchy_key in stg_keys:
                    default_stg = urun_hierarchy_key
                    st.info(f"✅ Bu ürün için STG bulundu")
                else:
                    default_stg = stg_keys[0] if stg_keys else None
                    st.warning("⚠️ Bu ürün için özel STG yok, başka hiyerarşi seçin")
                
                selected_stg_key = st.selectbox(
                    "STG Hiyerarşi",
                    stg_keys,
                    index=stg_keys.index(default_stg) if default_stg else 0,
                    format_func=lambda x: x.replace('_', ' > ')
                )
                
                stg_data = config['stg'][selected_stg_key]
                stg_coefficients = stg_data['coefficients']
                
                # Referans KTG seçimi
                stg_reference_ktg = st.selectbox(
                    "Referans KTG (STG için)",
                    list(stg_coefficients.keys())
                )
                
                if stg_reference_ktg:
                    st.info(f"Bu grupta ort. {stg_coefficients[stg_reference_ktg]:.1f} adet/hafta satılmış")
            else:
                st.warning("⚠️ STG hesaplanmamış. Önce Clustering modülünü kullanın.")
                stg_coefficients = None
                stg_reference_ktg = None
        
        with col_param4:
            haftalik_hedef = st.number_input(
                "Haftalık Hedef (Referans KTG için)",
                min_value=0.0,
                value=10.0,
                step=1.0,
                help="Referans KTG'deki bir mağazanın haftalık hedefi"
            )
            
            # Ürün ömrü
            col_omur1, col_omur2 = st.columns(2)
            with col_omur1:
                urun_omru_baslangic = st.number_input("Başlangıç Haftası", 1, 52, 1)
            with col_omur2:
                urun_omru_bitis = st.number_input("Bitiş Haftası", 1, 52, 52)
        
        # HESAPLA BUTONU
        st.divider()
        
        if st.button("🧮 Sipariş İhtiyacını Hesapla", type="primary", use_container_width=True):
            
            # Kontroller
            if not selected_ktgs:
                st.error("❌ En az bir KTG seçmelisiniz!")
            elif not carpan_values:
                st.error("❌ Çarpan seti seçilmedi!")
            elif not stg_coefficients or not stg_reference_ktg:
                st.error("❌ STG datası yok!")
            else:
                # Hesaplama
                with st.spinner("Hesaplanıyor..."):
                    toplam_siparis, ktg_detay = calculate_order_need(
                        selected_ktgs,
                        df_stores,
                        haftalik_hedef,
                        stg_reference_ktg,
                        stg_coefficients,
                        carpan_values,
                        urun_omru_baslangic - 1,  # 0-indexed
                        urun_omru_bitis - 1
                    )
                
                # Sonuçlar
                st.success("✅ Hesaplama Tamamlandı!")
                
                st.divider()
                st.subheader("📊 Sipariş İhtiyacı Sonuçları")
                
                # Toplam
                st.metric(
                    "🎯 TOPLAM SİPARİŞ İHTİYACI",
                    f"{int(toplam_siparis):,} adet",
                    help=f"{urun_omru_bitis - urun_omru_baslangic + 1} haftalık ürün ömrü için"
                )
                
                # KTG detayları
                st.markdown("#### KTG Bazında Dağılım")
                
                ktg_df = pd.DataFrame([
                    {
                        'KTG': ktg,
                        'Mağaza Sayısı': detay['magaza_sayisi'],
                        'STG Katsayısı': detay['stg_katsayisi'],
                        'Sipariş (adet)': int(detay['toplam'])
                    }
                    for ktg, detay in ktg_detay.items()
                ])
                
                st.dataframe(ktg_df, use_container_width=True, hide_index=True)
                
                # Özet bilgiler
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    st.metric("Toplam Mağaza", int(ktg_df['Mağaza Sayısı'].sum()))
                with col_sum2:
                    st.metric("Ürün Ömrü", f"{urun_omru_bitis - urun_omru_baslangic + 1} hafta")
                with col_sum3:
                    avg_per_store = toplam_siparis / ktg_df['Mağaza Sayısı'].sum() if ktg_df['Mağaza Sayısı'].sum() > 0 else 0
                    st.metric("Mağaza Başına Ort.", f"{avg_per_store:.1f} adet")
    
    else:
        # Ürün listesi tablosu
        st.dataframe(
            df_filtered[['SKU', 'Urun_Adi', 'Model_Kodu', 'Ana_Grup', 'Ust_Grup', 'Alt_Grup', 'Urun_Tipi', 'Brut_Marj_%']],
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    model_butce_module()
