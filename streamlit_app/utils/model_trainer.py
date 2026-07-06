import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

@st.cache_resource
def train_and_get_models(df_features):
    """
    Treina o modelo de agrupamento K-Means e o Random Forest preditivo 
    em tempo de execução, retornando os objetos ajustados.
    """
    if df_features.empty:
        return None, None, None, None
        
    df = df_features.copy()
    features_cluster = ["inc_media_100k", "açudes_canais_ha", "taxa_esgoto_media", "pop_media"]
    
    # 1. Padronização
    scaler = StandardScaler()
    dados_norm = scaler.fit_transform(df[features_cluster])
    
    # 2. Treinamento do K-Means (5 perfis de risco)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df["perfil_cluster"] = kmeans.fit_predict(dados_norm)
    
    # 3. Identificação automática do cluster de Alto Risco (o de maior incidência)
    cluster_alto_risco = df.groupby("perfil_cluster")["inc_media_100k"].mean().idxmax()
    df["alvo_alto_risco"] = (df["perfil_cluster"] == cluster_alto_risco).astype(int)
    
    # 4. Preparação da base balanceada para o Random Forest (Undersampling)
    alto_risco = df[df["alvo_alto_risco"] == 1]
    baixo_risco = df[df["alvo_alto_risco"] == 0]
    
    # Sorteamos uma quantidade menor de cidades de baixo risco (Proporção 1 para 2)
    # Se houver cidades suficientes, senao usamos todas disponiveis
    n_amostras = min(len(alto_risco) * 2, len(baixo_risco))
    baixo_risco_reduzido = baixo_risco.sample(n=n_amostras, random_state=42)
    
    df_treino_balanceado = pd.concat([alto_risco, baixo_risco_reduzido])
    
    X_train = df_treino_balanceado[["açudes_canais_ha", "taxa_esgoto_media", "pop_media", "natural_ha", "hydro_ha"]]
    y_train = df_treino_balanceado["alvo_alto_risco"]
    
    # 5. Treinamento do Random Forest
    rf = RandomForestClassifier(random_state=42, n_estimators=100)
    rf.fit(X_train, y_train)
    
    return rf, scaler, kmeans, df
