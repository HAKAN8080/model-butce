import pandas as pd
import streamlit as st
import os

def load_products():
    """Ürün master datasını yükle"""
    try:
        df = pd.read_csv('data/sample_products.csv', encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"Ürün datası yüklenemedi: {e}")
        return pd.DataFrame()

def load_stores():
    """Mağaza master datasını yükle"""
    try:
        df = pd.read_csv('data/sample_stores.csv', encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"Mağaza datası yüklenemedi: {e}")
        return pd.DataFrame()

def load_sales():
    """Satış datasını yükle"""
    try:
        df = pd.read_csv('data/sample_sales.csv', encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"Satış datası yüklenemedi: {e}")
        return pd.DataFrame()

def get_hierarchy_sales(df_sales, df_products, ana_grup=None, ust_grup=None, alt_grup=None):
    """Hiyerarşiye göre satış datasını filtrele ve haftalık topla"""
    
    # Ürünleri hiyerarşiye göre filtrele
    df_filtered = df_products.copy()
    
    if ana_grup:
        df_filtered = df_filtered[df_filtered['Ana_Grup'] == ana_grup]
    if ust_grup:
        df_filtered = df_filtered[df_filtered['Ust_Grup'] == ust_grup]
    if alt_grup:
        df_filtered = df_filtered[df_filtered['Alt_Grup'] == alt_grup]
    
    # Bu ürünlerin satışlarını getir
    filtered_skus = df_filtered['SKU'].unique()
    df_sales_filtered = df_sales[df_sales['SKU'].isin(filtered_skus)]
    
    # Haftalık topla
    haftalik_satis = df_sales_filtered.groupby('Hafta')['Satis_Adet'].sum().reset_index()
    haftalik_satis = haftalik_satis.sort_values('Hafta')
    
    return haftalik_satis

def get_product_sales(df_sales, model_kodu=None, sku=None):
    """Belirli bir model veya SKU için satış datasını getir"""
    
    if sku:
        df_filtered = df_sales[df_sales['SKU'] == sku]
    elif model_kodu:
        # Model koduna ait tüm SKU'ları bul
        df_products = load_products()
        skus = df_products[df_products['Model_Kodu'] == model_kodu]['SKU'].unique()
        df_filtered = df_sales[df_sales['SKU'].isin(skus)]
    else:
        return pd.DataFrame()
    
    # Haftalık topla
    haftalik_satis = df_filtered.groupby('Hafta')['Satis_Adet'].sum().reset_index()
    haftalik_satis = haftalik_satis.sort_values('Hafta')
    
    return haftalik_satis

def normalize_to_100(sales_values):
    """Satış değerlerini 0-100 arası normalize et"""
    if len(sales_values) == 0 or sales_values.max() == 0:
        return [0] * len(sales_values)
    
    return ((sales_values / sales_values.max()) * 100).tolist()
