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
def load_features_2011_2014():
    """Base de TREINO do modelo (período histórico de referência)."""
    path = NOTEBOOKS_DIR / "analise_geoespacial" / "dados_tratados_2011_2014.csv"
    if path.exists():
        return pd.read_csv(path)
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

@st.cache_data
def load_coord_lookup():
    """Tabela auxiliar code_muni -> (latitude, longitude) a partir da base geo do SINAN.

    Usada para posicionar os municípios das validações temporais no mapa, já que
    os CSVs de features não carregam coordenadas.
    """
    path = DATA_DIR / "processed" / "sinan_esq_processed_with_dt_notific_geo.parquet"
    if not path.exists():
        return pd.DataFrame(columns=["code_muni", "lat", "lon"])
    df = pd.read_parquet(path, columns=["ID_MUNICIP", "latitude_municipio", "longitude_municipio"])
    df = df.rename(columns={
        "ID_MUNICIP": "code_muni",
        "latitude_municipio": "lat",
        "longitude_municipio": "lon",
    })
    df["code_muni"] = df["code_muni"].astype(str).str[:6]
    df = df.dropna(subset=["lat", "lon"])
    return df.groupby("code_muni", as_index=False)[["lat", "lon"]].first()
