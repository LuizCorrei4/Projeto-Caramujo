import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.data_loader import load_features_2015_2019
from utils.model_trainer import train_and_get_models
import plotly.express as px

st.set_page_config(page_title="Simulador Preditivo", layout="wide")

st.title("Simulador Preditivo de Vulnerabilidade")

st.markdown("""
Esta ferramenta aplica algoritmos de Machine Learning (Floresta Aleatória) previamente treinados sobre a relação histórica entre dados de infraestrutura governamental e o balanço hídrico por satélite.

O objetivo do simulador é **prever de forma autônoma se um município hipotético (ou real) está enquadrado na classe de Alto Risco para infecção**, *sem depender do registro de casos da doença*. A IA toma a decisão baseando-se estritamente na geografia e no saneamento local.
""")

with st.spinner("Inicializando o motor de Machine Learning..."):
    df_features = load_features_2015_2019()
    rf_model, _, _, df_ml = train_and_get_models(df_features)

if rf_model is None:
    st.error("Erro estrutural: Falha na construção da árvore de decisão. Bases de dados ausentes.")
    st.stop()

# Configuração da Barra Lateral de Inputs
st.sidebar.header("Painel de Simulação")
st.sidebar.markdown("Configure os indicadores do cenário municipal desejado:")

pop = st.sidebar.number_input("População Estimada (Habitantes)", min_value=100, max_value=2000000, value=25000, step=1000)
esgoto = st.sidebar.slider("Índice de Coleta de Esgoto (%)", min_value=0.0, max_value=100.0, value=40.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Espelho Hídrico (MapBiomas - Hectares)**")
acudes = st.sidebar.slider("Açudes e Canais Artificiais (ha)", min_value=0.0, max_value=2000.0, value=50.0, step=5.0)
natural = st.sidebar.slider("Cursos d'Água Naturais (ha)", min_value=0.0, max_value=10000.0, value=150.0, step=50.0)
hydro = st.sidebar.slider("Grandes Represas de Usinas (ha)", min_value=0.0, max_value=10000.0, value=0.0, step=50.0)

# Processamento Preditivo
# A ordem das colunas DEVE ser idêntica ao que foi treinado:
# ["açudes_canais_ha", "taxa_esgoto_media", "pop_media", "natural_ha", "hydro_ha"]
dados_entrada = pd.DataFrame([{
    "açudes_canais_ha": acudes,
    "taxa_esgoto_media": esgoto,
    "pop_media": pop,
    "natural_ha": natural,
    "hydro_ha": hydro
}])

predicao = rf_model.predict(dados_entrada)[0]
probabilidades = rf_model.predict_proba(dados_entrada)[0]
prob_alto_risco = probabilidades[1]

st.header("Veredito Analítico do Sistema")

col_result, col_explicacao = st.columns(2)

with col_result:
    if predicao == 1:
        st.error(f"CLASSIFICAÇÃO: **ALTO RISCO EPIDEMIOLÓGICO**")
        st.markdown(f"**Confiança Estatística do Alerta:** {prob_alto_risco:.1%}")
    else:
        st.success(f"CLASSIFICAÇÃO: **BAIXO RISCO**")
        st.markdown(f"**Margem de Segurança Indicada:** {(1 - prob_alto_risco):.1%}")
        
    st.markdown("### Resumo do Cenário Inserido:")
    st.code(f"""
População: {pop:,} habitantes
Cobertura de Esgoto: {esgoto}%
Área de Açudes/Canais: {acudes} hectares
Hidrografia Natural: {natural} hectares
Massa de Hidrelétricas: {hydro} hectares
    """, language="yaml")

with col_explicacao:
    st.subheader("Transparência (Peso das Variáveis)")
    st.markdown("O gráfico ilustra matematicamente o peso relativo (Importância de Feature) de cada fator na decisão tomada pelo modelo de IA.")
    
    # Nomes traduzidos para facilitar a leitura
    nomes_legiveis = ["Açudes/Canais", "Taxa Esgoto", "População", "Água Natural", "Hidrelétricas"]
    importancias = pd.DataFrame({
        "Indicador Estrutural": nomes_legiveis,
        "Importância Relativa": rf_model.feature_importances_
    }).sort_values(by="Importância Relativa", ascending=True)
    
    fig_imp = px.bar(
        importancias, 
        x="Importância Relativa", 
        y="Indicador Estrutural", 
        orientation='h',
        color="Importância Relativa",
        color_continuous_scale="Blues"
    )
    fig_imp.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_imp, use_container_width=True)

st.divider()
st.markdown("""
> **Observação Técnica:** O peso descomunal da área hídrica de pequenos açudes frente ao abastecimento de esgoto é o que denominamos na pesquisa de **Paradoxo do Saneamento**. A ampliação descontrolada de água represada anula estatisticamente os investimentos municipais no combate a doenças de veiculação hídrica, elevando o nível do risco imediato.
""")
