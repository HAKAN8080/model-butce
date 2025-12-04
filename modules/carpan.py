import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from utils.data_loader import load_products, load_sales, get_hierarchy_sales, get_product_sales, normalize_to_100

def save_carpan_set(name, carpan_values, sezon, hierarchy_info):
    """Çarpan setini kaydet"""
    os.makedirs('saved_data/carpan_sets', exist_ok=True)
    
    data = {
        'name': name,
        'sezon': sezon,
        'hierarchy': hierarchy_info,
        'carpan_values': carpan_values
    }
    
    filename = f"saved_data/carpan_sets/{sezon}_{name}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_carpan_sets(sezon=None):
    """Kaydedilmiş çarpan setlerini yükle"""
    carpan_dir = 'saved_data/carpan_sets'
    if not os.path.exists(carpan_dir):
        return []
    
    sets = []
    for filename in os.listdir(carpan_dir):
        if filename.endswith('.json'):
            with open(os.path.join(carpan_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                if sezon is None or data.get('sezon') == sezon:
                    sets.append(data)
    
    return sets

def carpan_module():
    st.header("📊 Çarpan Modülü")
    st.markdown("Haftalık satış çarpanlarını belirleyin ve kaydedin.")
    
    # Veri yükleme
    df_products = load_products()
    df_sales = load_sales()
    
    if df_products.empty or df_sales.empty:
        st.error("Veri dosyaları yüklenemedi!")
        return
    
    # Sidebar - Ayarlar
    st.sidebar.subheader("Çarpan Ayarları")
    
    sezon = st.sidebar.text_input("Sezon", value="26SS", help="Örn: 26SS, 26FW")
    
    # Veri kaynağı seçimi
    veri_kaynagi = st.sidebar.radio(
        "Veri Kaynağı",
        ["Hiyerarşi", "Model/SKU"]
    )
    
    haftalik_satis = None
    hierarchy_info = {}
    
    if veri_kaynagi == "Hiyerarşi":
        # Hiyerarşi seçimi
        ana_grup = st.sidebar.selectbox("Ana Grup", [""] + sorted(df_products['Ana_Grup'].unique().tolist()))
        
        if ana_grup:
            ust_gruplar = sorted(df_products[df_products['Ana_Grup'] == ana_grup]['Ust_Grup'].unique().tolist())
            ust_grup = st.sidebar.selectbox("Üst Grup", [""] + ust_gruplar)
            
            if ust_grup:
                alt_gruplar = sorted(df_products[
                    (df_products['Ana_Grup'] == ana_grup) & 
                    (df_products['Ust_Grup'] == ust_grup)
                ]['Alt_Grup'].unique().tolist())
                alt_grup = st.sidebar.selectbox("Alt Grup", [""] + alt_gruplar)
                
                if alt_grup:
                    haftalik_satis = get_hierarchy_sales(df_sales, df_products, ana_grup, ust_grup, alt_grup)
                    hierarchy_info = {
                        'type': 'hiyerarşi',
                        'ana_grup': ana_grup,
                        'ust_grup': ust_grup,
                        'alt_grup': alt_grup
                    }
    else:
        # Model/SKU seçimi
        model_sku = st.sidebar.selectbox(
            "Model veya SKU Seç",
            [""] + sorted(df_products['Model_Kodu'].unique().tolist()) + sorted(df_products['SKU'].unique().tolist())
        )
        
        if model_sku:
            if model_sku.startswith('MDL'):
                haftalik_satis = get_product_sales(df_sales, model_kodu=model_sku)
                hierarchy_info = {'type': 'model', 'model_kodu': model_sku}
            else:
                haftalik_satis = get_product_sales(df_sales, sku=model_sku)
                hierarchy_info = {'type': 'sku', 'sku': model_sku}
    
    # Ana alan - Grafik ve düzenleme
    if haftalik_satis is not None and not haftalik_satis.empty:
        
        # Hafta listesi oluştur (52 hafta)
        all_weeks = [f"2024-W{str(i).zfill(2)}" for i in range(1, 53)]
        
        # Eksik haftaları 0 ile doldur
        haftalik_satis_full = pd.DataFrame({'Hafta': all_weeks})
        haftalik_satis_full = haftalik_satis_full.merge(haftalik_satis, on='Hafta', how='left')
        haftalik_satis_full['Satis_Adet'] = haftalik_satis_full['Satis_Adet'].fillna(0)
        
        # 0-100 skalaya normalize et
        normalized_values = normalize_to_100(haftalik_satis_full['Satis_Adet'].values)
        
        # Session state'de çarpan değerlerini sakla
        if 'carpan_values' not in st.session_state:
            st.session_state.carpan_values = normalized_values.copy()
        
        # İki kolon
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📈 Haftalık Satış Grafiği (100 Skala)")
            
            # Plotly grafiği
            fig = go.Figure()
            
            # Satış çizgisi
            fig.add_trace(go.Scatter(
                x=list(range(1, 53)),
                y=st.session_state.carpan_values,
                mode='lines+markers',
                name='Çarpan Değeri',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                height=500,
                xaxis_title="Hafta",
                yaxis_title="Değer (0-100)",
                hovermode='x unified',
                showlegend=True,
                yaxis=dict(range=[0, 120])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Düzenleme")
            
            # Hafta seçimi
            selected_week = st.number_input(
                "Hafta",
                min_value=1,
                max_value=52,
                value=1
            )
            
            # Değer düzenleme
            current_value = st.session_state.carpan_values[selected_week - 1]
            new_value = st.slider(
                "Çarpan Değeri",
                min_value=0.0,
                max_value=100.0,
                value=float(current_value),
                step=1.0,
                key=f"slider_{selected_week}"
            )
            
            if st.button("Güncelle"):
                st.session_state.carpan_values[selected_week - 1] = new_value
                st.rerun()
            
            st.divider()
            
            # Toplu işlemler
            st.markdown("**Toplu İşlemler**")
            
            baslangic_hafta = st.number_input("Başlangıç", 1, 52, 1)
            bitis_hafta = st.number_input("Bitiş", 1, 52, 52)
            carpan_oran = st.number_input("Çarpan %", -100, 200, 0)
            
            if st.button("Uygula"):
                for i in range(baslangic_hafta - 1, bitis_hafta):
                    current = st.session_state.carpan_values[i]
                    new = current * (1 + carpan_oran / 100)
                    st.session_state.carpan_values[i] = max(0, min(100, new))
                st.rerun()
            
            if st.button("Sıfırla"):
                st.session_state.carpan_values = normalized_values.copy()
                st.rerun()
        
        # Kaydetme bölümü
        st.divider()
        col_save1, col_save2, col_save3 = st.columns([2, 1, 1])
        
        with col_save1:
            carpan_name = st.text_input("Çarpan Set Adı", value=f"Çarpan_{sezon}")
        
        with col_save2:
            if st.button("💾 Kaydet", use_container_width=True):
                filename = save_carpan_set(
                    carpan_name,
                    st.session_state.carpan_values,
                    sezon,
                    hierarchy_info
                )
                st.success(f"✅ Kaydedildi: {filename}")
        
        with col_save3:
            # Kaydedilmiş setleri göster
            saved_sets = load_carpan_sets(sezon)
            if saved_sets:
                selected_set = st.selectbox(
                    "Yükle",
                    [""] + [s['name'] for s in saved_sets]
                )
                if selected_set:
                    loaded = next(s for s in saved_sets if s['name'] == selected_set)
                    st.session_state.carpan_values = loaded['carpan_values']
                    st.rerun()
    
    else:
        st.info("👈 Lütfen soldaki menüden veri kaynağı seçin")

if __name__ == "__main__":
    carpan_module()
