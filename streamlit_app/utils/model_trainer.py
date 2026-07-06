import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Colunas que alimentam cada etapa (idênticas ao notebook de modelagem)
FEATURES_CLUSTER = ["inc_media_100k", "açudes_canais_ha", "taxa_esgoto_media", "pop_media"]
FEATURES_RF = ["açudes_canais_ha", "taxa_esgoto_media", "pop_media", "natural_ha", "hydro_ha"]

# Nomes legíveis usados na interface
NOMES_FEATURES_RF = ["Açudes/Canais", "Taxa Esgoto", "População", "Água Natural", "Hidrelétricas"]


def _rotular_clusters(df):
    """Traduz os rótulos numéricos do K-Means em perfis ecológicos legíveis.

    A tradução é feita de forma DINÂMICA (pelas características de cada grupo), e não
    por número fixo, porque o índice do cluster não carrega significado por si só.
    Regras derivadas dos achados do notebook de modelagem:
      - maior incidência média        -> Epicentros da Doença (Alto Risco)
      - maior população média          -> Grandes Metrópoles (outliers demográficos)
      - maior área de açudes/canais    -> Centros com Grandes Represas (ponto cego do satélite)
      - dos 2 restantes: maior cobertura de esgoto -> Centros Urbanos Intermediários
                         menor cobertura de esgoto  -> Cinturão de Vulnerabilidade
    """
    stats = df.groupby("perfil_cluster")[FEATURES_CLUSTER + ["natural_ha", "hydro_ha"]].mean()
    nomes = {}

    cluster_epicentro = stats["inc_media_100k"].idxmax()
    nomes[cluster_epicentro] = "Epicentros da Doença (Alto Risco)"

    restantes = stats.drop(index=cluster_epicentro)
    cluster_metropole = restantes["pop_media"].idxmax()
    nomes[cluster_metropole] = "Grandes Metrópoles"

    restantes = restantes.drop(index=cluster_metropole)
    cluster_represa = restantes["açudes_canais_ha"].idxmax()
    nomes[cluster_represa] = "Centros com Grandes Represas"

    restantes = restantes.drop(index=cluster_represa)
    # Sobram 2: separa por cobertura de esgoto
    ordenados = restantes["taxa_esgoto_media"].sort_values(ascending=False)
    nomes[ordenados.index[0]] = "Centros Urbanos Intermediários"
    nomes[ordenados.index[1]] = "Cinturão de Vulnerabilidade"

    return nomes


@st.cache_resource
def train_reference_model(df_train):
    """Treina o modelo de REFERÊNCIA sobre a base histórica (2011-2014).

    Retorna um dicionário com os objetos ajustados (scaler, kmeans, rf), o índice
    do cluster de alto risco, o dicionário de nomes semânticos e a própria base de
    treino já rotulada. Este é o "modelo campeão" reaplicado nos períodos futuros.
    """
    if df_train is None or df_train.empty:
        return None

    df = df_train.copy()

    # 1. Padronização
    scaler = StandardScaler()
    dados_norm = scaler.fit_transform(df[FEATURES_CLUSTER])

    # 2. K-Means (5 perfis de risco)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df["perfil_cluster"] = kmeans.fit_predict(dados_norm)

    # 3. Cluster de alto risco = o de maior incidência média
    cluster_alto_risco = df.groupby("perfil_cluster")["inc_media_100k"].mean().idxmax()
    df["alvo_alto_risco"] = (df["perfil_cluster"] == cluster_alto_risco).astype(int)

    nomes_clusters = _rotular_clusters(df)
    df["perfil_nome"] = df["perfil_cluster"].map(nomes_clusters)

    # 4. Base balanceada para o Random Forest (Undersampling 1:2)
    alto_risco = df[df["alvo_alto_risco"] == 1]
    baixo_risco = df[df["alvo_alto_risco"] == 0]
    n_amostras = min(len(alto_risco) * 2, len(baixo_risco))
    baixo_risco_reduzido = baixo_risco.sample(n=n_amostras, random_state=42)
    df_balanceado = pd.concat([alto_risco, baixo_risco_reduzido])

    # 5. Random Forest treinado SEM variáveis clínicas (só ambiente + saneamento)
    rf = RandomForestClassifier(random_state=42, n_estimators=100)
    rf.fit(df_balanceado[FEATURES_RF], df_balanceado["alvo_alto_risco"])

    return {
        "scaler": scaler,
        "kmeans": kmeans,
        "rf": rf,
        "cluster_alto_risco": cluster_alto_risco,
        "nomes_clusters": nomes_clusters,
        "df_train": df,
    }


@st.cache_data
def apply_model_to_period(_model, df_period):
    """Aplica o modelo de referência (2011-2014) a um período futuro (out-of-time).

    Cruza duas leituras para cada município:
      - alvo_alto_risco  : a "realidade" do período (K-Means sobre a incidência observada)
      - predicao_rf      : o alerta do modelo (Random Forest, só com ambiente/saneamento)
    e classifica cada município numa 'situacao' interpretável.
    """
    if _model is None or df_period is None or df_period.empty:
        return pd.DataFrame()

    df = df_period.copy()
    scaler = _model["scaler"]
    kmeans = _model["kmeans"]
    rf = _model["rf"]
    cluster_ar = _model["cluster_alto_risco"]

    # Realidade observada no período (via K-Means na incidência real)
    dados_norm = scaler.transform(df[FEATURES_CLUSTER])
    df["perfil_cluster"] = kmeans.predict(dados_norm)
    df["alvo_alto_risco"] = (df["perfil_cluster"] == cluster_ar).astype(int)

    # Previsão do modelo (sem olhar casos/incidência)
    df["predicao_rf"] = rf.predict(df[FEATURES_RF])
    df["prob_alto_risco"] = rf.predict_proba(df[FEATURES_RF])[:, 1]

    def _situacao(row):
        real, prev = row["alvo_alto_risco"], row["predicao_rf"]
        if real == 1 and prev == 1:
            return "Alto risco confirmado"
        if real == 0 and prev == 1:
            return "Foco emergente (alerta preventivo)"
        if real == 1 and prev == 0:
            return "Alto risco não detectado"
        return "Baixo risco"

    df["situacao"] = df.apply(_situacao, axis=1)
    return df
