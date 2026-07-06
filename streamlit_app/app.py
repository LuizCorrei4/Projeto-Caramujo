import streamlit as st

st.set_page_config(
    page_title="Sistema de Vigilância: Projeto Caramujo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Sistema de Inteligência Socioambiental para Prevenção da Esquistossomose")

st.markdown("""
A esquistossomose é uma doença parasitária cuja transmissão está intimamente ligada a vulnerabilidades socioambientais, especialmente à falta de saneamento adequado e à presença de coleções hídricas antrópicas (pequenos açudes e canais) utilizadas pelas populações locais para trabalho e subsistência.

Este sistema integra dados epidemiológicos (Ministério da Saúde - SINAN), hidrológicos (MapBiomas), censitários (IBGE) e de infraestrutura sanitária (SNIS) para monitorar, identificar e prever focos de alto risco da doença no território nacional.

### Estrutura do Sistema

Navegue pelas opções no menu lateral para acessar os módulos analíticos:

1. **Painel Epidemiológico:** Explore o histórico descritivo de casos notificados, avalie a progressão cronológica da incidência da doença e entenda o perfil demográfico (idade, sexo, escolaridade) das populações mais afetadas.
2. **Mapeamento e Perfis:** Visualize a disposição geográfica dos polos de risco e o mapeamento dos 5 Perfis de Vulnerabilidade descobertos pelo nosso modelo estatístico não-supervisionado (K-Means). Esta página evidencia como o fornecimento nominal de saneamento não assegura o controle da doença em ambientes de forte exploração hídrica.
3. **Aplicação Temporal do Modelo:** Veja o modelo preditivo (Random Forest) em ação. Treinado sobre a base histórica de 2011–2014 exclusivamente com fatores físicos e infraestruturais, ele é aplicado "às cegas" nos horizontes de 2015–2019 e 2020–2025, revelando os focos de alto risco confirmados e, sobretudo, os **focos emergentes** — municípios que carregam a assinatura ambiental de risco e são candidatos a se tornarem os próximos epicentros.

---

> **Aviso Técnico:** Esta é uma aplicação demonstrativa desenvolvida a partir dos dados abertos, focada na prospecção arquitetural epidemiológica do *Projeto Caramujo*. Os dados processados podem estar anonimizados ou restringidos geograficamente para os escopos de análise do repositório base.
""")

st.info("Para iniciar, expanda a barra lateral esquerda (se estiver oculta) e selecione o primeiro módulo analítico.")
