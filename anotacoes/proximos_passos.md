# Roteiro: Integração de Dados Espaciais (IBGE/geobr) com SINAN

Este roteiro detalha os passos para traduzir códigos de municípios, extrair coordenadas (Latitude e Longitude) e cruzar com os dados de esquistossomose para análises espaciais.

## Passo 0: Preparação do Ambiente
Antes de iniciar, garanta que as bibliotecas necessárias para manipulação de dados espaciais estão instaladas no seu ambiente.

```bash
pip install geobr geopandas shapely matplotlib
```

## Passo 1: Baixar a Malha Municipal do IBGE
Utilizaremos o `geobr` para carregar a base completa de municípios do Brasil. Isso servirá como nosso "dicionário" de códigos e base cartográfica.
```python
import geobr
import pandas as pd
import warnings

# Oculta avisos inofensivos de projeção do geopandas
warnings.filterwarnings('ignore')

print("Baixando malha municipal do IBGE...")
# Baixa todos os municípios do Brasil (ano base 2020)
df_mapa = geobr.read_municipality(code_muni="all", year=2020)

# O dataframe retornará colunas como:
# 'code_muni' (Código IBGE), 'name_muni' (Nome), 'abbrev_state' (UF) e 'geometry' (Polígono)
```

## Passo 2: Extrair Coordenadas (Latitude e Longitude)
A partir do polígono da cidade (`geometry`), vamos calcular o ponto central (centroide) para extrair as coordenadas X e Y.
```python
print("Calculando centroides e extraindo coordenadas...")

# Calcula o ponto central de cada município
df_mapa['centroide'] = df_mapa['geometry'].centroid

# Extrai a Longitude (Eixo X) e a Latitude (Eixo Y)
df_mapa['longitude'] = df_mapa['centroide'].x
df_mapa['latitude'] = df_mapa['centroide'].y
```

## Passo 3: Agrupar os Casos de Esquistossomose
Agora precisamos preparar a base limpa do SINAN para cruzar com o mapa, agrupando o número de casos por município.
```python
# Suponha que df_sinan seja o seu DataFrame já processado
# Agrupa os dados e conta os casos por município
df_casos_por_cidade = df_sinan.groupby('ID_MN_RESI').size().reset_index(name='total_casos')

# IMPORTANTE: Alinhamento das chaves
# O SINAN frequentemente usa códigos de 6 dígitos, enquanto o IBGE usa 7 dígitos.
# Vamos garantir que o tipo seja string e cortar o código do IBGE para 6 dígitos para o merge.
df_casos_por_cidade['ID_MN_RESI'] = df_casos_por_cidade['ID_MN_RESI'].astype(str)
df_mapa['code_muni_str'] = df_mapa['code_muni'].astype(str).str[:6]