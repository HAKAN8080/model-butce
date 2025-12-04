import streamlit as st
import pandas as pd
import json
import os
from utils.data_loader import load_stores, load_products, load_sales
from utils.calculations import calculate_stg_coefficients

def save_ktg_stg_config(ktg_data, stg_data):
    """KTG ve STG yapılandırmasını kaydet"""
    os.makedirs('saved_data/ktg_stg', exist_ok=True)
    
    data = {
        'ktg': ktg_data,
        'stg': stg_data
    }
    
    filename = 'saved_data/ktg_stg/config.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_ktg_stg_config():
    """KTG ve STG yapılandırmasını yükle"""
    filename = 'saved_data/ktg_stg/config.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def clustering_module():
    st.header("🎯 Clustering Modülü")
    st.markdown("Mağaza gruplarını (KTG) ve satış trend gruplarını (STG) yönetin.")
    
    # Veri yükleme
    df_stores = load_stores()
    df_products = load_products()
    df_sales = load_sales()
    
    if df_stores.empty:
        st.error("Mağaza datası yüklenemedi!")
        return
    
    # Tab yapısı
    tab1, tab2 = st.tabs(["KTG - Kapasite Trend Grup", "STG - Satış Trend Grup"])
    
    # ===== TAB 1: KTG =====
    with tab1:
        st.subheader("Kapasite Trend Grup (KTG)")
        st.markdown("Mağazalar kapasite ve satış hızına göre 9 gruba ayrılır.")
        
        # KTG gruplarını göster
        ktg_groups = ['Büyük-Hızlı', 'Büyük-Orta', 'Büyük-Yavaş',
                      'Normal-Hızlı', 'Normal-Orta', 'Normal-Yavaş',
                      'Küçük-Hızlı', 'Küçük-Orta', 'Küçük-Yavaş']
        
        # KTG dağılımını göster
        st.markdown("#### 📊 Mevcut KTG Dağılımı")
        
        ktg_summary = df_stores.groupby('KTG').agg({
            'Magaza_Kodu': 'count',
            'M2': 'mean'
        }).round(0)
        ktg_summary.columns = ['Mağaza Sayısı', 'Ort. m²']
        
        # Tüm KTG'leri göster
        for ktg in ktg_groups:
            if ktg in ktg_summary.index:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{ktg}**")
                with col2:
                    st.metric("Mağaza", int(ktg_summary.loc[ktg, 'Mağaza Sayısı']))
                with col3:
                    st.metric("Ort. m²", int(ktg_summary.loc[ktg, 'Ort. m²']))
        
        st.divider()
        
        # Mağaza detayları
        st.markdown("#### 🏪 Mağaza Detayları")
        
        selected_ktg = st.selectbox(
            "KTG Seç",
            ktg_groups
        )
        
        if selected_ktg:
            df_filtered = df_stores[df_stores['KTG'] == selected_ktg]
            st.dataframe(
                df_filtered[['Magaza_Kodu', 'Magaza_Adi', 'Sehir', 'M2']],
                use_container_width=True,
                hide_index=True
            )
    
    # ===== TAB 2: STG =====
    with tab2:
        st.subheader("Satış Trend Grup (STG)")
        st.markdown("Hiyerarşi bazında her KTG için ortalama haftalık satış katsayılarını hesaplayın.")
        
        if df_products.empty or df_sales.empty:
            st.warning("STG hesaplaması için ürün ve satış datası gerekli!")
            return
        
        # Hiyerarşi seçimi
        st.markdown("#### 📁 Hiyerarşi Seç")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ana_grup = st.selectbox(
                "Ana Grup",
                [""] + sorted(df_products['Ana_Grup'].unique().tolist()),
                key="stg_ana"
            )
        
        with col2:
            if ana_grup:
                ust_gruplar = sorted(df_products[df_products['Ana_Grup'] == ana_grup]['Ust_Grup'].unique().tolist())
                ust_grup = st.selectbox("Üst Grup", [""] + ust_gruplar, key="stg_ust")
            else:
                ust_grup = None
        
        with col3:
            if ana_grup and ust_grup:
                alt_gruplar = sorted(df_products[
                    (df_products['Ana_Grup'] == ana_grup) & 
                    (df_products['Ust_Grup'] == ust_grup)
                ]['Alt_Grup'].unique().tolist())
                alt_grup = st.selectbox("Alt Grup", [""] + alt_gruplar, key="stg_alt")
            else:
                alt_grup = None
        
        # STG Hesapla
        if ana_grup and ust_grup and alt_grup:
            if st.button("🔄 STG Hesapla", type="primary"):
                with st.spinner("Hesaplanıyor..."):
                    stg_coefficients = calculate_stg_coefficients(
                        df_sales, df_products, df_stores,
                        ana_grup, ust_grup, alt_grup
                    )
                    
                    if stg_coefficients:
                        st.session_state.current_stg = {
                            'hierarchy': {
                                'ana_grup': ana_grup,
                                'ust_grup': ust_grup,
                                'alt_grup': alt_grup
                            },
                            'coefficients': stg_coefficients
                        }
                        st.success("✅ STG katsayıları hesaplandı!")
                    else:
                        st.error("Bu hiyerarşi için yeterli satış datası bulunamadı.")
        
        # STG sonuçlarını göster
        if 'current_stg' in st.session_state:
            st.divider()
            st.markdown("#### 📊 STG Katsayıları")
            
            stg_data = st.session_state.current_stg
            st.info(f"**Hiyerarşi:** {stg_data['hierarchy']['ana_grup']} > {stg_data['hierarchy']['ust_grup']} > {stg_data['hierarchy']['alt_grup']}")
            
            # Tablo olarak göster
            stg_df = pd.DataFrame([
                {'KTG': ktg, 'Ort. Haftalık Satış': round(val, 2)}
                for ktg, val in stg_data['coefficients'].items()
            ]).sort_values('Ort. Haftalık Satış', ascending=False)
            
            st.dataframe(stg_df, use_container_width=True, hide_index=True)
            
            # Kaydet butonu
            if st.button("💾 STG Kaydet"):
                # Mevcut config'i yükle veya yeni oluştur
                config = load_ktg_stg_config() or {'ktg': {}, 'stg': {}}
                
                # STG'yi ekle
                hierarchy_key = f"{ana_grup}_{ust_grup}_{alt_grup}"
                config['stg'][hierarchy_key] = stg_data
                
                # Kaydet
                save_ktg_stg_config(config['ktg'], config['stg'])
                st.success("✅ STG kaydedildi!")
        
        # Kaydedilmiş STG'leri göster
        st.divider()
        st.markdown("#### 📚 Kaydedilmiş STG'ler")
        
        config = load_ktg_stg_config()
        if config and config.get('stg'):
            for key, stg_data in config['stg'].items():
                with st.expander(f"📁 {key.replace('_', ' > ')}"):
                    stg_df = pd.DataFrame([
                        {'KTG': ktg, 'Ort. Haftalık Satış': round(val, 2)}
                        for ktg, val in stg_data['coefficients'].items()
                    ])
                    st.dataframe(stg_df, use_container_width=True, hide_index=True)
        else:
            st.info("Henüz kaydedilmiş STG yok.")

if __name__ == "__main__":
    clustering_module()
