# Detalhes: Enriquecimento geografico e analise temporal

Base atual: data/processed/sinan_esq_processed_with_dt_notific_geo.parquet

## Requisitos
- pandas
- geobr
- geopandas
- shapely
- matplotlib (ou seaborn)

## 1) Carregar a base enriquecida
```python
import pandas as pd

df = pd.read_parquet("../data/processed/sinan_esq_processed_with_dt_notific_geo.parquet")
```

## 2) Analise temporal basica (serie mensal)
```python
df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")
df = df[df["DT_NOTIFIC"].notna()].copy()

df["mes"] = df["DT_NOTIFIC"].dt.to_period("M").dt.to_timestamp()
serie_mes = df.groupby("mes").size().reset_index(name="casos")

df["SG_UF"] = df["SG_UF"].astype("string").str.upper()
serie_mes_uf = df.groupby(["mes", "SG_UF"]).size().reset_index(name="casos")
```

Plot rapido (matplotlib):
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4))
plt.plot(serie_mes["mes"], serie_mes["casos"])
plt.title("Serie mensal de casos (DT_NOTIFIC)")
plt.xlabel("Mes")
plt.ylabel("Casos")
plt.tight_layout()
```

## 3) Tabelas finais para analise
```python
ag_mensal = df.groupby("mes").size().reset_index(name="casos")
ag_mensal_uf = df.groupby(["mes", "SG_UF"]).size().reset_index(name="casos")
ag_municipio = df.groupby("ID_MUNICIP").size().reset_index(name="casos")

ag_mensal.to_csv("../data/processed/esq_series_mensal.csv", index=False)
ag_mensal_uf.to_csv("../data/processed/esq_series_mensal_uf.csv", index=False)
ag_municipio.to_csv("../data/processed/esq_casos_municipio.csv", index=False)
```

## 4) Mapa do Brasil (focos por municipio)
Mesmo com lat/long na base, o mapa por municipio precisa da geometria do geobr.

```python
import geobr
import geopandas as gpd

ag_municipio = df.groupby("ID_MUNICIP").size().reset_index(name="casos")
ag_municipio["ID_MUNICIP"] = ag_municipio["ID_MUNICIP"].astype("string").str.zfill(6)

gdf = geobr.read_municipality(code_muni="all", year=2020)
gdf["code_muni_str"] = gdf["code_muni"].astype("string").str[:6]

gdf_plot = gdf.merge(
    ag_municipio,
    left_on="code_muni_str",
    right_on="ID_MUNICIP",
    how="left",
)

gdf_plot["casos"] = gdf_plot["casos"].fillna(0)

ax = gdf_plot.plot(
    column="casos",
    cmap="Reds",
    linewidth=0.1,
    figsize=(10, 10),
    legend=True,
)
ax.set_title("Focos de esquistossomose por municipio (DT_NOTIFIC)")
ax.set_axis_off()
```

## Observacoes
- ID_MUNICIP e SG_UF originais devem ser mantidos para rastreio.
- Para graficos de pontos (scatter), usar latitude_municipio e longitude_municipio.
- Se precisar dos centroides, converter o GeoDataFrame para EPSG:4674 antes de calcular.
