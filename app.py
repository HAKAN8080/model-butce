import streamlit as st
from modules.carpan import carpan_module
from modules.clustering import clustering_module
from modules.model_butce import model_butce_module

# Sayfa yapılandırması
st.set_page_config(
    page_title="Model Bütçe - Thorius AR4U",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stil
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Başlık
    st.title("📊 Model Bütçe - Sipariş İhtiyaç Planlama")
    st.markdown("**Thorius AR4U Platform** - Retail Analytics")
    
    # Sidebar navigasyon
    st.sidebar.title("🧭 Navigasyon")
    
    menu = st.sidebar.radio(
        "Modül Seç",
        ["🏠 Ana Sayfa", "📊 Çarpan Modülü", "🎯 Clustering", "💼 Model Bütçe"],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    
    # Bilgi
    st.sidebar.markdown("### 💡 Bilgi")
    st.sidebar.info("""
    **Model Bütçe Sistemi**
    
    1️⃣ **Çarpan:** Haftalık satış çarpanlarını belirleyin
    
    2️⃣ **Clustering:** KTG ve STG gruplarını oluşturun
    
    3️⃣ **Model Bütçe:** Sipariş ihtiyacını hesaplayın
    """)
    
    # Modül yönlendirme
    if menu == "🏠 Ana Sayfa":
        show_home()
    elif menu == "📊 Çarpan Modülü":
        carpan_module()
    elif menu == "🎯 Clustering":
        clustering_module()
    elif menu == "💼 Model Bütçe":
        model_butce_module()

def show_home():
    st.header("🏠 Ana Sayfa")
    
    st.markdown("""
    ## Hoş Geldiniz! 👋
    
    Model Bütçe sistemi, retail operasyonları için sipariş ihtiyacını belirlemeye yönelik 
    kapsamlı bir planlama platformudur.
    
    ### 📋 Modüller
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📊 Çarpan Modülü
        - Haftalık satış çarpanları
        - İnteraktif grafik düzenleme
        - Sezon bazlı kayıt
        - Hiyerarşi/Model bazlı
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Clustering
        - **KTG:** 9 mağaza grubu
        - **STG:** Satış trend katsayıları
        - Hiyerarşi bazlı hesaplama
        - Kapasite optimizasyonu
        """)
    
    with col3:
        st.markdown("""
        #### 💼 Model Bütçe
        - Ürün listesi ve filtreleme
        - KTG seçimi
        - STG bazlı genişletme
        - Sipariş ihtiyacı hesaplama
        """)
    
    st.divider()
    
    st.markdown("""
    ### 🎯 Hesaplama Formülü
    
    ```
    Toplam Sipariş = Σ (Mağaza Sayısı × Haftalık Hedef × STG Katsayısı × Çarpan × Ürün Ömrü)
    ```
    
    ### 🚀 Başlangıç Adımları
    
    1. **Çarpan Modülü:** Sezon için çarpan setlerini oluşturun
    2. **Clustering:** STG katsayılarını hesaplayın (hiyerarşi bazında)
    3. **Model Bütçe:** Ürünler için sipariş ihtiyacını hesaplayın
    
    ### 📊 Veri Yapısı
    
    - **Ürünler:** ~130 SKU (örnek veri)
    - **Mağazalar:** 39 mağaza, 9 KTG grubu
    - **Satış Datası:** 52 haftalık geçmiş
    
    ### 🔧 Ürün Tipleri
    
    - **Carryover:** Mevsimsel devam eden ürünler
    - **NOS:** Never Out of Stock - Hiç tükenmemesi gerekenler
    - **Yeni:** Yeni ürün lansmanları
    """)
    
    st.divider()
    
    # Sistem durumu
    st.markdown("### 📈 Sistem Durumu")
    
    import os
    from utils.data_loader import load_products, load_stores, load_sales
    from modules.carpan import load_carpan_sets
    from modules.clustering import load_ktg_stg_config
    
    col_status1, col_status2, col_status3, col_status4 = st.columns(4)
    
    with col_status1:
        df_products = load_products()
        st.metric("Ürün Sayısı", len(df_products) if not df_products.empty else 0)
    
    with col_status2:
        df_stores = load_stores()
        st.metric("Mağaza Sayısı", len(df_stores) if not df_stores.empty else 0)
    
    with col_status3:
        carpan_sets = load_carpan_sets()
        st.metric("Çarpan Set", len(carpan_sets))
    
    with col_status4:
        config = load_ktg_stg_config()
        stg_count = len(config.get('stg', {})) if config else 0
        st.metric("STG Hiyerarşi", stg_count)

if __name__ == "__main__":
    main()
