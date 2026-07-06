import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.data_loader import load_features_2015_2019, load_geo_data
from utils.model_trainer import train_and_get_models

st.set_page_config(page_title="Mapeamento e Perfis", layout="wide")

st.title("Mapeamento Espacial e Perfis de Vulnerabilidade")

st.markdown("""
Esta seção explora a distribuição territorial da esquistossomose e revela os perfis de vulnerabilidade socioambiental 
descobertos pela inteligência artificial. 

O objetivo analítico desta aba é demonstrar graficamente o **Paradoxo do Saneamento**: o fornecimento de 
rede de esgoto é fundamental, porém não é suficiente para impedir epidemias locais se o município apresentar forte disponibilidade hídrica antrópica (pequenos açudes e canais agrícolas de contato constante).
""")

# Carregamento da inteligência de perfis
with st.spinner("Processando agrupamento de risco socioambiental (K-Means)..."):
    df_features = load_features_2015_2019()
    _, _, kmeans, df_ml = train_and_get_models(df_features)

if df_ml is None or df_ml.empty:
    st.error("Falha ao processar a base de dados socioambiental (MapBiomas/SNIS/IBGE).")
    st.stop()

# Converte o código numérico do grupo para string visando melhor plotagem categórica
df_ml["perfil_cluster"] = "Perfil " + df_ml["perfil_cluster"].astype(str)

st.header("1. O Paradoxo do Saneamento na Prática")

col1, col2 = st.columns([6, 4])

with col1:
    fig_disp = px.scatter(
        df_ml,
        x="taxa_esgoto_media",
        y="inc_media_100k",
        size="pop_media",
        color="perfil_cluster",
        hover_name="municipality",
        hover_data=["state", "açudes_canais_ha"],
        log_y=True,
        title="Avaliação Direta: Esgoto vs. Incidência de Contaminação",
        labels={
            "taxa_esgoto_media": "Taxa de Esgoto Nominal (%)",
            "inc_media_100k": "Incidência Média (Escala Log)",
            "perfil_cluster": "Perfil de Agrupamento"
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_disp, use_container_width=True)

with col2:
    st.markdown("""
    **Interpretação do Gráfico:**
    
    - Observe como certos municípios avançam substancialmente no eixo horizontal (possuem 60%, 70% ou 80% de saneamento básico declarado).
    - Entretanto, ao invés de sua incidência (eixo vertical) despencar, eles se mantêm no ápice dos índices de contaminação.
    
    A resposta estatística se encontra nos perfis marcados. Quando investigamos o "Perfil de Alto Risco" (Epicentros), nota-se que a falha reside nos dados não-convencionais. O cruzamento espacial identificou que é a presença densa de **açudes e canais** que sequestra os benefícios da infraestrutura local.
    """)

st.divider()

st.header("2. Avaliação Comparativa de Infraestrutura e Hidrografia")
st.markdown("Distribuição matemática (Quartis e Mediana) das variáveis cruciais dentro de cada Perfil Identificado.")

col_box1, col_box2 = st.columns(2)

with col_box1:
    fig_box_agua = px.box(
        df_ml, 
        x="perfil_cluster", 
        y="açudes_canais_ha", 
        color="perfil_cluster",
        title="Distribuição Hídrica: Área de Açudes e Canais (Hectares)",
        log_y=True,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_box_agua, use_container_width=True)

with col_box2:
    fig_box_esgoto = px.box(
        df_ml, 
        x="perfil_cluster", 
        y="taxa_esgoto_media", 
        color="perfil_cluster",
        title="Distribuição Estrutural: Taxa de Coleta de Esgoto (%)",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_box_esgoto, use_container_width=True)

st.divider()

st.header("3. Distribuição Geográfica de Focos")
st.markdown("Visão macro do posicionamento territorial dos focos confirmados no Brasil (com base em centroides municipais).")

with st.spinner("Carregando malha geográfica..."):
    df_geo = load_geo_data()

if not df_geo.empty and 'latitude_municipio' in df_geo.columns and 'longitude_municipio' in df_geo.columns:
    df_map = df_geo.groupby(['ID_MUNICIP', 'latitude_municipio', 'longitude_municipio']).size().reset_index(name='Casos Registrados')
    df_map = df_map.rename(columns={'latitude_municipio': 'lat', 'longitude_municipio': 'lon'})
    
    fig_map = px.scatter_mapbox(
        df_map, 
        lat="lat", 
        lon="lon", 
        size="Casos Registrados",
        color="Casos Registrados", 
        color_continuous_scale="Reds", 
        zoom=3.5, 
        center={"lat": -14.235, "lon": -51.925},
        mapbox_style="carto-positron",
        title="Volume de Notificações por Coordernada Municipal"
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Não foram encontrados dados válidos de latitude e longitude na base enriquecida para plotagem gráfica do mapa.")
