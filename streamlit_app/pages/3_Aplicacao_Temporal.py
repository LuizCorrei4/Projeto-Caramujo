import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.data_loader import (
    load_features_2011_2014,
    load_features_2015_2019,
    load_features_2020_2025,
)
from utils.model_trainer import train_reference_model, apply_model_to_period

st.set_page_config(page_title="Aplicação Temporal do Modelo", layout="wide")

st.title("Aplicação Temporal do Modelo (Validação Out-of-Time)")

st.markdown("""
Um modelo preventivo só tem valor se enxerga o **futuro**. Aqui congelamos o modelo aprendido na base histórica de
**2011–2014** (K-Means + Random Forest, treinado *sem nenhum dado clínico*) e o aplicamos "às cegas" sobre dois
horizontes seguintes — **2015–2019** e **2020–2025** — sem jamais deixá-lo reaprender.

Para cada município comparamos duas leituras:

- 🩺 **Realidade do período** — o que efetivamente aconteceu (K-Means sobre a incidência observada).
- 🤖 **Alerta do modelo** — o que o Random Forest previu olhando **apenas** ambiente e saneamento.

O cruzamento revela não só os acertos, mas os **focos emergentes**: municípios que o modelo classificou como alto
risco "por engano" (falsos positivos) — só que, justamente por carregarem a assinatura ambiental perigosa, muitos
deles são **candidatos reais a se tornarem os próximos epicentros**. Esse é o Mapa de Vigilância Ativa.
""")

# ---------------------------------------------------------------------------
# Modelo de referência (treino 2011-2014)
# ---------------------------------------------------------------------------
with st.spinner("Treinando o modelo de referência (2011-2014)..."):
    df_train = load_features_2011_2014()
    model = train_reference_model(df_train)

if model is None:
    st.error(
        "Não foi possível treinar o modelo de referência. "
        "Verifique se `dados_tratados_2011_2014.csv` existe em `notebooks/analise_geoespacial/`."
    )
    st.stop()

n_treino_ar = int(model["df_train"]["alvo_alto_risco"].sum())
st.caption(
    f"Modelo de referência treinado sobre **{len(model['df_train'])} municípios** de 2011–2014, "
    f"com **{n_treino_ar} epicentros** de alto risco como linha de base."
)

# ---------------------------------------------------------------------------
# Seleção do horizonte futuro
# ---------------------------------------------------------------------------
periodo = st.radio(
    "Selecione o horizonte de aplicação:",
    ["2015 – 2019", "2020 – 2025"],
    horizontal=True,
)

if periodo == "2015 – 2019":
    df_periodo = load_features_2015_2019()
else:
    df_periodo = load_features_2020_2025()

df = apply_model_to_period(model, df_periodo)

if df.empty:
    st.error("Base do período selecionado indisponível.")
    st.stop()

# ---------------------------------------------------------------------------
# Métricas de desempenho
# ---------------------------------------------------------------------------
n_reais = int((df["alvo_alto_risco"] == 1).sum())
n_previstos = int((df["predicao_rf"] == 1).sum())
n_confirmados = int((df["situacao"] == "Alto risco confirmado").sum())
n_emergentes = int((df["situacao"] == "Foco emergente (alerta preventivo)").sum())
n_perdidos = int((df["situacao"] == "Alto risco não detectado").sum())
acuracia = (df["alvo_alto_risco"] == df["predicao_rf"]).mean()

st.header(f"Desempenho da aplicação em {periodo}")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Alto risco real (período)", n_reais, help="Epicentros efetivamente observados (K-Means sobre a incidência real).")
m2.metric("Alertas do modelo", n_previstos, help="Municípios que o Random Forest apontou como alto risco.")
m3.metric("✅ Confirmados", n_confirmados, help="Epicentros reais que o modelo acertou.")
m4.metric("🟠 Focos emergentes", n_emergentes, help="Falsos positivos: assinatura ambiental de risco sem surto (ainda). Candidatos a vigilância.")
m5.metric("Acurácia global", f"{acuracia:.1%}")

if n_perdidos > 0:
    st.warning(
        f"⚠️ {n_perdidos} município(s) de alto risco real **não** foram capturados pelo modelo "
        f"(falsos negativos) — dinâmicas locais surgidas após 2014 que a base histórica não previa."
    )
else:
    st.success("✅ Nenhum falso negativo: todo epicentro real do período foi antecipado pelo modelo.")

st.divider()

# ---------------------------------------------------------------------------
# Matriz de confusão + tabela de focos emergentes
# ---------------------------------------------------------------------------
col_cm, col_tab = st.columns([4, 6])

with col_cm:
    st.subheader("Matriz de Confusão")
    st.caption(f"Modelo de 2011–2014 testado em {periodo}.")
    tn = int(((df["alvo_alto_risco"] == 0) & (df["predicao_rf"] == 0)).sum())
    fp = int(((df["alvo_alto_risco"] == 0) & (df["predicao_rf"] == 1)).sum())
    fn = int(((df["alvo_alto_risco"] == 1) & (df["predicao_rf"] == 0)).sum())
    tp = int(((df["alvo_alto_risco"] == 1) & (df["predicao_rf"] == 1)).sum())

    z = [[tn, fp], [fn, tp]]
    fig_cm = go.Figure(data=go.Heatmap(
        z=z,
        x=["Previsto: Baixo", "Previsto: Alto"],
        y=["Real: Baixo", "Real: Alto"],
        text=[[f"{tn}", f"{fp}"], [f"{fn}", f"{tp}"]],
        texttemplate="%{text}",
        textfont={"size": 20},
        colorscale="Blues",
        showscale=False,
    ))
    fig_cm.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0}, height=320, yaxis={"autorange": "reversed"})
    st.plotly_chart(fig_cm, use_container_width=True)
    st.caption(
        "O quadrante laranja da vida real — os **falsos positivos** (canto superior direito) — é o que a saúde "
        "pública lê como vigilância preventiva, não como erro."
    )

with col_tab:
    st.subheader("🟠 Focos emergentes — candidatos a próximos epicentros")
    st.caption(
        "Municípios que o modelo classificou como alto risco e que **ainda não** eram epicentros no período — "
        "ordenados pela extensão de açudes/canais, o principal fator ambiental de risco."
    )
    df_fp = df[df["situacao"] == "Foco emergente (alerta preventivo)"].copy()
    df_fp = df_fp[[
        "municipality", "state", "inc_media_100k", "taxa_esgoto_media", "açudes_canais_ha"
    ]].rename(columns={
        "municipality": "Município",
        "state": "Estado",
        "inc_media_100k": "Incidência (100k)",
        "taxa_esgoto_media": "Esgoto (%)",
        "açudes_canais_ha": "Açudes/Canais (ha)",
    }).sort_values("Açudes/Canais (ha)", ascending=False)

    st.dataframe(
        df_fp.style.format({
            "Incidência (100k)": "{:.1f}",
            "Esgoto (%)": "{:.1f}",
            "Açudes/Canais (ha)": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
        height=320,
    )

st.divider()
st.markdown("""
> **Leitura epidemiológica.** Diferente da ciência de dados purista — onde um falso positivo é ruído a ser
> minimizado —, na vigilância em saúde pública o falso positivo é o produto mais valioso: um município que
> **ainda não** explodiu, mas cujo ambiente já grita risco. Antecipar-se a ele é exatamente o propósito
> preventivo deste sistema.
""")
