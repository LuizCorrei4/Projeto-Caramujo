import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

# Permite acesso relativo seguro ao pacote utils
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.data_loader import load_sinan_data

st.set_page_config(page_title="Painel Epidemiológico", layout="wide")

st.title("Painel Epidemiológico e Descritivo")

st.markdown("Monitoramento histórico e avaliação demográfica das notificações de Esquistossomose baseadas exclusivamente na base de casos confirmados e tratados do SINAN.")

with st.spinner("Carregando base de notificações (SINAN)..."):
    df = load_sinan_data()

if df.empty:
    st.error("Não foi possível carregar a base de dados epidemiológica (SINAN). Verifique a disponibilidade dos arquivos processados.")
    st.stop()

# Filtros laterais
st.sidebar.header("Filtros de Análise")
estados_disponiveis = df['SG_UF'].dropna().unique().tolist()
estados_selecionados = st.sidebar.multiselect("Filtrar por Estado (UF):", options=sorted(estados_disponiveis), default=[])

anos_disponiveis = df['ano'].dropna().unique()
ano_min, ano_max = int(min(anos_disponiveis)), int(max(anos_disponiveis))
ano_selecionado = st.sidebar.slider("Período de Análise (Anos):", ano_min, ano_max, (ano_min, ano_max))

# Aplicando os filtros ao dataframe
df_filtrado = df[(df['ano'] >= ano_selecionado[0]) & (df['ano'] <= ano_selecionado[1])]
if estados_selecionados:
    df_filtrado = df_filtrado[df_filtrado['SG_UF'].isin(estados_selecionados)]

# Seção de Métricas Principais (KPIs)
st.subheader("Visão Geral do Período Selecionado")
col1, col2, col3, col4 = st.columns(4)

total_casos = len(df_filtrado)
col1.metric("Total de Casos Confirmados", f"{total_casos:,}")

if 'IDADE_PROCESSADA' in df_filtrado.columns:
    idade_media = df_filtrado['IDADE_PROCESSADA'].mean()
    col2.metric("Média de Idade (Anos)", f"{idade_media:.1f}")
else:
    col2.metric("Média de Idade", "ND")

# Taxa de evolução para cura. Baseado no dicionário: Ficha 1 = Cura
cura = df_filtrado[df_filtrado['EVOLUCAO'] == '1'].shape[0] if 'EVOLUCAO' in df_filtrado.columns else 0
taxa_cura = (cura / total_casos * 100) if total_casos > 0 else 0
col3.metric("Recuperação/Cura Aparente", f"{taxa_cura:.1f}%")

cidades_afetadas = df_filtrado['ID_MUNICIP'].nunique()
col4.metric("Municípios Contaminados", f"{cidades_afetadas}")

st.divider()

# Seção Gráfica
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Evolução Temporal (Incidência Bruta)")
    casos_por_ano = df_filtrado.groupby('ano').size().reset_index(name='Casos')
    fig_temporal = px.line(
        casos_por_ano, x='ano', y='Casos', markers=True, 
        color_discrete_sequence=["#1f77b4"],
        labels={'ano': 'Ano de Notificação', 'Casos': 'Volume de Casos'}
    )
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    st.subheader("Nível de Escolaridade")
    if 'CS_ESCOL_N' in df_filtrado.columns:
        escol = df_filtrado['CS_ESCOL_N'].value_counts().reset_index()
        escol.columns = ['Escolaridade (Código)', 'Casos']
        fig_escol = px.bar(
            escol, x='Escolaridade (Código)', y='Casos', 
            color_discrete_sequence=["#2ca02c"]
        )
        st.plotly_chart(fig_escol, use_container_width=True)

with col_dir:
    st.subheader("Perfil Demográfico: Distribuição Etária")
    if 'IDADE_PROCESSADA' in df_filtrado.columns and 'CS_SEXO' in df_filtrado.columns:
        fig_idade = px.histogram(
            df_filtrado, x='IDADE_PROCESSADA', color='CS_SEXO', 
            nbins=30, barmode="group",
            color_discrete_map={'M': '#1f77b4', 'F': '#ff7f0e'},
            labels={'IDADE_PROCESSADA': 'Faixa Etária', 'CS_SEXO': 'Sexo Biológico'}
        )
        st.plotly_chart(fig_idade, use_container_width=True)
        
    st.subheader("Composição Racial das Notificações")
    if 'CS_RACA' in df_filtrado.columns:
        raca = df_filtrado['CS_RACA'].value_counts().reset_index()
        raca.columns = ['Raça (Código)', 'Casos']
        fig_raca = px.pie(
            raca, values='Casos', names='Raça (Código)', 
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_raca, use_container_width=True)
