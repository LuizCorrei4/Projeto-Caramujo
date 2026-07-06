import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

@st.cache_data
def load_sinan_data():
    path = DATA_DIR / "processed" / "sinan_esq_processed_with_dt_notific.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        df['ano'] = df['DT_NOTIFIC'].dt.year
        return df
    return pd.DataFrame()

@st.cache_data
def load_geo_data():
    path = DATA_DIR / "processed" / "sinan_esq_processed_with_dt_notific_geo.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        df['ano'] = df['DT_NOTIFIC'].dt.year
        return df
    return pd.DataFrame()

@st.cache_data
def load_features_2015_2019():
    path = NOTEBOOKS_DIR / "analise_geoespacial" / "dados_tratados_2015_2019.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
    
@st.cache_data
def load_features_2020_2025():
    path = NOTEBOOKS_DIR / "analise_geoespacial" / "dados_tratados_2020_2025.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
