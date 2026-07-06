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

# Mapeamento semântico dos Clusters conforme achados do notebook de modelagem
mapa_clusters = {
    '0': 'Centros Urbanos Intermediários',
    '1': 'Cinturão de Vulnerabilidade',
    '2': 'Epicentros da Doença (Alto Risco)',
    '3': 'Grandes Metrópoles',
    '4': 'Centros com Grandes Represas'
}
df_ml["perfil_cluster"] = df_ml["perfil_cluster"].astype(str).map(mapa_clusters)

st.header("1. O Paradoxo do Saneamento na Prática")

col1, col2 = st.columns([6, 4])

with col1:
    fig_disp = px.scatter(
        df_ml,
        x="taxa_esgoto_media",
        y="inc_media_100k",
        size="pop_media",
        hover_name="municipality",
        hover_data=["state", "açudes_canais_ha", "perfil_cluster"],
        log_y=True,
        title="Avaliação Direta: Esgoto vs. Incidência de Contaminação",
        labels={
            "taxa_esgoto_media": "Taxa de Esgoto Nominal (%)",
            "inc_media_100k": "Incidência Média (Escala Log)"
        },
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig_disp, use_container_width=True)

with col2:
    st.markdown("""
    **Interpretação do Gráfico (Ausência de Correlação Linear):**
    
    A premissa clássica de saúde pública sugere que o aumento da rede de esgoto deveria reduzir linearmente as doenças de veiculação hídrica. No entanto, o gráfico ao lado prova matematicamente que **não há correlação linear forte** entre saneamento básico isolado e incidência de contaminação para a esquistossomose.
    
    - Observe como certos municípios avançam substancialmente no eixo horizontal (possuem 60%, 70% ou 80% de saneamento básico declarado).
    - Entretanto, ao invés de sua incidência (eixo vertical) despencar, eles se mantêm no ápice absoluto de contaminação.
    
    Este é o **Paradoxo do Saneamento**: o cruzamento espacial identificou que é a presença densa de **pequenos açudes e canais antrópicos** (onde há forte contato humano) que neutraliza os benefícios da infraestrutura local, sequestrando as métricas tradicionais de saúde.
    """)

st.divider()

st.header("2. Avaliação Comparativa de Infraestrutura e Hidrografia (Clusters)")
st.markdown("""
O algoritmo K-Means agrupou os municípios em 5 perfis ecológicos e socioeconômicos distintos:
- **Centros Urbanos Intermediários:** Municípios de médio porte com boa estrutura e baixa incidência.
- **Cinturão de Vulnerabilidade:** Gargalos de saneamento com populações vulneráveis e presença de doença.
- **Epicentros da Doença (Alto Risco):** Municípios pequenos onde a incidência epidemiológica extrema coexiste com fortes concentrações de águas rasas, revelando o pico do risco.
- **Grandes Metrópoles:** Outliers demográficos onde a densidade habitacional gigantesca dilui a incidência da doença.
- **Centros com Grandes Represas:** "Pontos cegos" de satélite; municípios com enormes lâminas d'água (hidrelétricas) que não servem como vetor por serem profundas, isolando a transmissão.

Abaixo, analisamos a distribuição destas variáveis dentro de cada perfil.
""")

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
