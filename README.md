# Projeto Caramujo - Esquistossomose

Analise exploratoria e pipeline de preprocessamento de dados de esquistossomose, com notebooks e dados auxiliares.

## Estrutura

- `src/pipeline/`: pipeline modular de preprocessamento.
- `src/pipeline/steps/`: etapas numeradas do pipeline.
- `src/geo_enrich/`: enriquecimento geografico (nomes de municipio/UF e lat/long).
- `notebooks/`: notebooks de AED e preprocessamento.
- `notebooks/analise_geoespacial/`: notebooks de validacao e analise espacial.
- `data/`: dados locais (somente `sinan_esqu_raw.parquet` deve ser versionado).
- `data/processed/`: saidas locais do pipeline (nao versionar).
- `anotacoes/`: dicionario de dados e notas.
- `images/`: imagens geradas para relatorios ou notebooks.

## Pipeline de preprocessamento

### Arquitetura

- Entrada: `data/sinan_esqu_raw.parquet`
- Saida: `data/processed/sinan_esqu_processed.parquet`
- Orquestracao: `src/pipeline/run_pipeline.py`
- Etapas:
	- `00_fetch_raw.py`
	- `01_load_and_filter.py`
	- `02_clean_and_impute.py`
	- `03_feature_engineering.py`
	- `04_export.py`

### Decisoes (em construcao)

- Descarte imediato: regras baseadas em `anotacoes/descarte_imediato.txt` (sera formalizado no pipeline).
- Nulos: mediana para numericos; moda para categoricos; remocao condicional de linhas criticas.
- Feature engineering: idade, atrasos temporais e datas derivadas.
- Outliers: filtro IQR conservador (1.5) para numericos e pos-features temporais.
- Escolaridade: `CS_ESCOL_N` normalizada para 0-10 antes do mapeamento de ignorados.

## Como executar (pipeline)

Requisitos: Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m pipeline.run_pipeline
```

## Tutorial completo do pipeline (src)

### 0) Baixar dados via pysus (opcional)

Use quando quiser baixar o bruto direto do SINAN e salvar em `data/sinan_esqu_raw.parquet`.

```bash
export PYTHONPATH=src
python -m pipeline.run_pipeline --download-raw
```

Para baixar apenas o bruto, sem rodar o restante do pipeline:

```bash
export PYTHONPATH=src
python -m pipeline.fetch_raw_sinan
```

### 1) Preparar dados de entrada

- O arquivo bruto esperado por padrao e `data/sinan_esqu_raw.parquet`.
- Se quiser usar outro caminho/arquivo, utilize `--input` (ver exemplos abaixo).

### 2) Executar com configuracao padrao

```bash
export PYTHONPATH=src
python -m pipeline.run_pipeline
```

Saida padrao: `data/processed/sinan_esqu_processed.parquet`.
Durante a execucao, o pipeline imprime contagens por etapa.

### 3) Principais parametros via CLI

- `--input`: caminho do parquet bruto (default: `data/sinan_esqu_raw.parquet`).
- `--output`: caminho do parquet processado (default: `data/processed/sinan_esqu_processed.parquet`).
- `--download-raw`: baixa dados via pysus antes de rodar o pipeline.
- `--dis-code`: codigos da doenca separados por virgula (default: `ESQU`).
- `--no-positive-filter`: desativa o filtro de casos positivos. Por padrao, filtra `AN_QUALI == "1"`.
- `--positive-column`: coluna usada no filtro de positivos (default: `AN_QUALI`).
- `--positive-value`: valor considerado positivo (default: `1`).
- `--no-target-filter`: desativa o filtro baseado no alvo (`EVOLUCAO`).
	- Quando desativado, o alvo nao e normalizado nem filtrado por codigos invalidos.
	- Os valores em `target_drop_values` (ex.: `"4"`) nao sao removidos.
	- A coluna alvo pode entrar na imputacao (mediana/moda) caso esteja com NA.
- `--no-drop-after-features`: mantem colunas originais apos o feature engineering.

Se precisar mudar regras fixas (colunas descartadas, datas, codigos ignorados,
faixas de idade, etc.), edite `src/pipeline/config.py`.

### 4) Exemplos de uso

```bash
# usar outro arquivo de entrada e saida
PYTHONPATH=src python -m pipeline.run_pipeline \
	--input data/sinan_esqu.csv \
	--output data/processed/sinan_esqu_custom.parquet

# baixar bruto via pysus e rodar o pipeline
PYTHONPATH=src python -m pipeline.run_pipeline --download-raw

# baixar bruto com codigo customizado
PYTHONPATH=src python -m pipeline.run_pipeline --download-raw --dis-code ESQU

# executar sem filtro de casos positivos
PYTHONPATH=src python -m pipeline.run_pipeline --no-positive-filter

# desativar filtro do alvo (EVOLUCAO)
PYTHONPATH=src python -m pipeline.run_pipeline --no-target-filter

# trocar coluna e valor do filtro de positivos
PYTHONPATH=src python -m pipeline.run_pipeline \
	--positive-column AN_QUALI \
	--positive-value 1

# manter colunas originais apos feature engineering
PYTHONPATH=src python -m pipeline.run_pipeline --no-drop-after-features

# gerar processado com DT_NOTIFIC
PYTHONPATH=src python -m pipeline.run_pipeline \
	--output data/processed/sinan_esq_processed_with_dt_notific.parquet
```

## Enriquecimento geografico (geo_enrich)

Script: [src/geo_enrich/enrich_geo.py](src/geo_enrich/enrich_geo.py)

Como rodar:
```bash
PYTHONPATH=src python -m geo_enrich.enrich_geo \
	--input data/processed/sinan_esq_processed_with_dt_notific.parquet \
	--output data/processed/sinan_esq_processed_with_dt_notific_geo.parquet
```

## Notebooks

- [notebooks/AED_Esquistossomose_Final.ipynb](notebooks/AED_Esquistossomose_Final.ipynb): analise exploratoria final.
- [notebooks/esqu_preprocess_FINAL.ipynb](notebooks/esqu_preprocess_FINAL.ipynb): preprocessamento dos dados.
- [notebooks/analise_geoespacial/EDA_esq_processed.ipynb](notebooks/analise_geoespacial/EDA_esq_processed.ipynb): EDA da base processada com DT_NOTIFIC.
- [notebooks/analise_geoespacial/validacao_e_analise_temporal_basica](notebooks/analise_geoespacial/validacao_e_analise_temporal_basica): validacao e analise temporal basica.

## Documentacao

- `anotacoes/dicionario.md`: dicionario de variaveis e codigos.

## Dados

Somente `data/sinan_esqu_raw.parquet` deve ser versionado. Os demais arquivos em `data/` sao considerados locais.

Se algum arquivo de `data/` ja estiver no Git, remova-o do indice antes de publicar:

```bash
git rm --cached data/arquivo_que_nao_deve_subir
```

## Licenca

MIT. Veja `LICENSE`.
