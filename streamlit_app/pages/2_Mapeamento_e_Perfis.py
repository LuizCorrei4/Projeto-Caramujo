import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.data_loader import load_features_2011_2014, load_geo_data
from utils.model_trainer import train_reference_model

st.set_page_config(page_title="Mapeamento e Perfis", layout="wide")

st.title("Mapeamento Espacial e Perfis de Vulnerabilidade")

st.markdown("""
Esta seção explora a distribuição territorial da esquistossomose e revela os **perfis de vulnerabilidade
socioambiental** descobertos pela inteligência artificial sobre a base histórica de referência (**2011–2014**).

O objetivo analítico é demonstrar graficamente o **Paradoxo do Saneamento**: o fornecimento de rede de esgoto é
fundamental, porém não é suficiente para impedir epidemias locais se o município apresentar forte disponibilidade
hídrica antrópica (pequenos açudes e canais agrícolas de contato constante).
""")

# Carregamento da inteligência de perfis (modelo de referência 2011-2014)
with st.spinner("Processando agrupamento de risco socioambiental (K-Means)..."):
    df_features = load_features_2011_2014()
    model = train_reference_model(df_features)

if model is None:
    st.error(
        "Falha ao processar a base de dados socioambiental (MapBiomas/SNIS/IBGE). "
        "Verifique se o arquivo `dados_tratados_2011_2014.csv` existe em `notebooks/analise_geoespacial/`."
    )
    st.stop()

# Cópia de trabalho (NUNCA mutar o objeto retornado pelo cache_resource)
df_ml = model["df_train"].copy()

st.header("1. O Paradoxo do Saneamento na Prática")

col1, col2 = st.columns([6, 4])

with col1:
    fig_disp = px.scatter(
        df_ml,
        x="taxa_esgoto_media",
        y="inc_media_100k",
        size="pop_media",
        color="perfil_nome",
        hover_name="municipality",
        hover_data=["state", "açudes_canais_ha"],
        log_y=True,
        title="Avaliação Direta: Esgoto vs. Incidência de Contaminação",
        labels={
            "taxa_esgoto_media": "Taxa de Esgoto Nominal (%)",
            "inc_media_100k": "Incidência Média (Escala Log)",
            "perfil_nome": "Perfil de Risco",
        },
    )
    fig_disp.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.45))
    st.plotly_chart(fig_disp, use_container_width=True)

with col2:
    st.markdown("""
    **Interpretação do Gráfico (Ausência de Correlação Linear):**

    A premissa clássica de saúde pública sugere que o aumento da rede de esgoto deveria reduzir linearmente as
    doenças de veiculação hídrica. No entanto, o gráfico ao lado prova matematicamente que **não há correlação
    linear forte** entre saneamento básico isolado e incidência de contaminação para a esquistossomose.

    - Observe como certos municípios avançam substancialmente no eixo horizontal (possuem 60%, 70% ou 80% de
      saneamento básico declarado).
    - Entretanto, ao invés de sua incidência (eixo vertical) despencar, eles se mantêm no ápice absoluto de
      contaminação (perfil **Epicentros da Doença**).

    Este é o **Paradoxo do Saneamento**: o cruzamento espacial identificou que é a presença densa de **pequenos
    açudes e canais antrópicos** (onde há forte contato humano) que neutraliza os benefícios da infraestrutura
    local, sequestrando as métricas tradicionais de saúde.
    """)

st.divider()

st.header("2. Os 5 Perfis de Risco descobertos pelo K-Means")
st.markdown("""
Para evitar poluir a análise com cidades onde a transmissão é inviável, o agrupamento considerou apenas os
**municípios historicamente ativos** (pelo menos 1 caso positivo confirmado e dados de saneamento válidos).
Sobre eles, o algoritmo **K-Means (K = 5)** — que agrupa municípios por semelhança matemática, sem supervisão
humana — separou o país em cinco perfis ecológicos e socioeconômicos distintos:
""")

# Descrições dos perfis (ordenadas por incidência média, do mais crítico ao menos)
descricoes = {
    "Epicentros da Doença (Alto Risco)": "Municípios pequenos onde a incidência epidemiológica extrema coexiste com fortes concentrações de águas rasas (açudes/canais). É o pico do risco — a classe-alvo que o modelo aprende a reconhecer.",
    "Cinturão de Vulnerabilidade": "Gargalos de saneamento, com populações vulneráveis e presença consolidada da doença. Prioridade estrutural de infraestrutura.",
    "Centros Urbanos Intermediários": "Municípios de médio porte, com estrutura sanitária razoável e incidência mais baixa.",
    "Centros com Grandes Represas": "\"Pontos cegos\" do satélite: municípios com enormes espelhos d'água antrópicos (açudes/canais em larga escala), mas que — até o período — registraram baixa incidência. A abundância hídrica captada pelo satélite ainda não se converteu em surto.",
    "Grandes Metrópoles": "Outliers demográficos: a densidade habitacional gigantesca dilui a incidência proporcional da doença.",
}

# Ordena os perfis por incidência média decrescente para a apresentação
ordem_perfis = (
    df_ml.groupby("perfil_nome")["inc_media_100k"].mean().sort_values(ascending=False).index.tolist()
)

resumo = (
    df_ml.groupby("perfil_nome")
    .agg(
        Municipios=("municipality", "count"),
        Incidencia_media_100k=("inc_media_100k", "mean"),
        Esgoto_medio=("taxa_esgoto_media", "mean"),
        Acudes_canais_ha=("açudes_canais_ha", "mean"),
        Pop_media=("pop_media", "mean"),
    )
    .reindex(ordem_perfis)
    .round(1)
)

for perfil in ordem_perfis:
    with st.expander(f"**{perfil}**  —  {int(resumo.loc[perfil, 'Municipios'])} municípios", expanded=(perfil == ordem_perfis[0])):
        st.markdown(descricoes.get(perfil, ""))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Incidência média (100k)", f"{resumo.loc[perfil, 'Incidencia_media_100k']:.1f}")
        c2.metric("Esgoto médio", f"{resumo.loc[perfil, 'Esgoto_medio']:.1f}%")
        c3.metric("Açudes/Canais (ha)", f"{resumo.loc[perfil, 'Acudes_canais_ha']:.1f}")
        c4.metric("População média", f"{resumo.loc[perfil, 'Pop_media']:,.0f}")

st.divider()

st.header("3. Análise das Distribuições por Perfil")
st.markdown("""
Os boxplots abaixo mostram como cada variável se distribui **dentro de cada perfil**, revelando o que
matematicamente distingue um grupo do outro. A caixa concentra os 50% centrais dos municípios (do 1º ao 3º
quartil), a linha interna é a mediana e os pontos isolados são valores extremos. Escala logarítmica é usada
onde a amplitude é muito grande.
""")

variaveis_box = [
    ("inc_media_100k", "Incidência por 100 mil habitantes", True),
    ("taxa_esgoto_media", "Taxa de Coleta de Esgoto (%)", False),
    ("açudes_canais_ha", "Área de Açudes e Canais (ha)", True),
    ("pop_media", "População Média", True),
]

box_col1, box_col2 = st.columns(2)
for idx, (coluna, titulo, log) in enumerate(variaveis_box):
    destino = box_col1 if idx % 2 == 0 else box_col2
    with destino:
        fig_box = px.box(
            df_ml,
            x="perfil_nome",
            y=coluna,
            color="perfil_nome",
            title=titulo,
            log_y=log,
            category_orders={"perfil_nome": ordem_perfis},
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_box.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="",
            xaxis={"tickangle": -25},
            margin={"t": 40},
        )
        st.plotly_chart(fig_box, use_container_width=True)

st.divider()

st.header("4. Consulta de Municípios por Perfil")
perfil_escolhido = st.selectbox("Selecione um perfil para listar os municípios:", ordem_perfis)
busca = st.text_input("Filtrar por nome do município (opcional):", "")

tabela = df_ml[df_ml["perfil_nome"] == perfil_escolhido].copy()
if busca:
    tabela = tabela[tabela["municipality"].str.contains(busca, case=False, na=False)]

tabela = tabela[[
    "municipality", "state", "inc_media_100k", "taxa_esgoto_media", "açudes_canais_ha", "pop_media"
]].rename(columns={
    "municipality": "Município",
    "state": "Estado",
    "inc_media_100k": "Incidência (100k)",
    "taxa_esgoto_media": "Esgoto (%)",
    "açudes_canais_ha": "Açudes/Canais (ha)",
    "pop_media": "População média",
}).sort_values("Incidência (100k)", ascending=False)

st.dataframe(tabela, use_container_width=True, hide_index=True)

st.divider()

st.header("5. Distribuição Geográfica de Focos")
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
        title="Volume de Notificações por Coordenada Municipal",
    )
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Não foram encontrados dados válidos de latitude e longitude na base enriquecida para plotagem gráfica do mapa.")
