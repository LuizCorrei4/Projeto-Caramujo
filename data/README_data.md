# Dados (data/)

Este arquivo descreve as colunas presentes nos arquivos de dados em data/, como cada artefato foi gerado e quais colunas foram removidas no processamento.

## Como os dados em data/ foram gerados

Os comandos abaixo usam a CLI principal do projeto com `PYTHONPATH=src`. Quando um parametro nao for informado, vale o padrao definido em `src/pipeline/config.py` ou nos scripts de `src/geo_enrich/`.

| Artefato | Comando de origem | Parametros que importam | Observacoes |
| --- | --- | --- | --- |
| `data/sinan_esqu_raw.parquet` | `PYTHONPATH=src python -m pipeline.run_pipeline --download-raw --dis-code ESQU` | `--dis-code` pode receber uma lista separada por virgula; `--input` define o caminho onde o bruto sera salvo. | O Step 00 baixa os arquivos do SINAN via `pysus` e grava o bruto. |
| `data/processed/sinan_esqu_processed.parquet` | `PYTHONPATH=src python -m pipeline.run_pipeline` | Usa `--input data/sinan_esqu_raw.parquet` e `--output data/processed/sinan_esqu_processed.parquet` por padrao. | Aplica filtros de positivos, filtro do alvo, limpeza, imputacao, IQR e descarte pos-features. |
| `data/processed/sinan_esqu_unsup.parquet` | `PYTHONPATH=src python -m pipeline.run_pipeline --cohort-profile unsupervised-ml` | Usa `--input data/sinan_esqu_raw.parquet` e, quando `--output` nao e informado, grava em `data/processed/sinan_esqu_unsup.parquet` por padrao. | Mantem todas as evolucoes do caso, remove apenas `AN_QUALI = 2`, preserva `AN_QUALI = 3` e valores em branco como ausentes, e reutiliza limpeza/imputacao/IQR do pipeline atual. |
| `data/processed/sinan_esq_processed_with_dt_notific.parquet` | `PYTHONPATH=src python -m pipeline.run_pipeline --input data/sinan_esqu_raw.parquet --output data/processed/sinan_esq_processed_with_dt_notific.parquet` | Para reproduzir este arquivo, `DT_NOTIFIC` precisa sair da lista `DROP_AFTER_FEATURES` em `src/pipeline/config.py`. | `--no-drop-after-features` nao e equivalente, porque preserva todas as colunas pos-features. |
| `data/processed/sinan_esq_processed_with_dt_notific_geo.parquet` | `PYTHONPATH=src python -m geo_enrich.enrich_geo --input data/processed/sinan_esq_processed_with_dt_notific.parquet --output data/processed/sinan_esq_processed_with_dt_notific_geo.parquet` | `--year 2020` por padrao, `--id-column ID_MUNICIP`, `--keep-geometry` opcional. | Adiciona nome do municipio, UF e centroides com base no `geobr`. |
| `data/populacao/ufs/pop_ufs_YYYY.parquet` | `PYTHONPATH=src python -m geo_enrich.population_tables --input data/processed/sinan_esq_processed_with_dt_notific_geo.parquet --output-dir data/populacao/ufs` | `--years` e opcional; sem ele, os anos sao inferidos a partir de `DT_NOTIFIC`. | Gera uma tabela por ano e salva um arquivo por UF/ano. |

## Arquivos

- `sinan_esqu_raw.parquet`: dados brutos baixados do SINAN.
- `processed/sinan_esqu_processed.parquet`: base processada para analise/modelagem, sem `DT_NOTIFIC`.
- `processed/sinan_esqu_unsup.parquet`: base processada para ML nao supervisionado, com todas as evolucoes e sem casos com `AN_QUALI = 2`.
- `processed/sinan_esq_processed_with_dt_notific.parquet`: variante do processado mantendo `DT_NOTIFIC`.
- `processed/sinan_esq_processed_with_dt_notific_geo.parquet`: variante enriquecida com nome do municipio, UF e lat/long.
- `populacao/ufs/`: tabelas de populacao por UF e ano.


## sinan_esqu_raw.parquet (53 colunas)

Colunas presentes:
- TP_NOT
- ID_AGRAVO
- DT_NOTIFIC
- SEM_NOT
- NU_ANO
- SG_UF_NOT
- ID_MUNICIP
- ID_REGIONA
- ID_UNIDADE
- DT_SIN_PRI
- SEM_PRI
- ANO_NASC
- NU_IDADE_N
- CS_SEXO
- CS_GESTANT
- CS_RACA
- CS_ESCOL_N
- SG_UF
- ID_MN_RESI
- ID_RG_RESI
- ID_PAIS
- DT_INVEST
- ID_OCUPA_N
- DT_COPRO
- AN_QUANT
- OUTROS
- TRATAM
- TRATANAO
- STCURA1
- STCURA2
- STCURA3
- FORMA
- TPAUTOCTO
- COUFINF
- COPAISINF
- COMUNINF
- NOPROPIN
- NOCOLINF
- DOENCA_TRA
- EVOLUCAO
- DT_ENCERRA
- DT_DIGITA
- DT_TRANSUS
- DT_TRANSDM
- DT_TRANSSM
- DT_TRANSRS
- DT_TRANSSE
- DT_OBITO
- DS_FORMA
- AN_QUALI
- DTTRAT
- DT_RESU3
- OUTRO_EX

## processed/sinan_esqu_processed.parquet (16 colunas)

Colunas presentes:
- ID_MUNICIP
- ID_UNIDADE
- CS_SEXO
- CS_GESTANT
- CS_RACA
- CS_ESCOL_N
- SG_UF
- TRATAM
- FORMA
- COUFINF
- DOENCA_TRA
- EVOLUCAO
- AN_QUALI
- IDADE_PROCESSADA
- delay_notificacao_dias
- tempo_encerramento_dias

## processed/sinan_esq_processed_with_dt_notific.parquet (17 colunas)

Colunas presentes:
- DT_NOTIFIC
- ID_MUNICIP
- ID_UNIDADE
- CS_SEXO
- CS_GESTANT
- CS_RACA
- CS_ESCOL_N
- SG_UF
- TRATAM
- FORMA
- COUFINF
- DOENCA_TRA
- EVOLUCAO
- AN_QUALI
- IDADE_PROCESSADA
- delay_notificacao_dias
- tempo_encerramento_dias

## Colunas removidas no processamento (40 colunas)

Removidas do bruto para o processado:
- TP_NOT
- ID_AGRAVO
- DT_NOTIFIC
- SEM_NOT
- NU_ANO
- SG_UF_NOT
- ID_REGIONA
- DT_SIN_PRI
- SEM_PRI
- ANO_NASC
- NU_IDADE_N
- ID_MN_RESI
- ID_RG_RESI
- ID_PAIS
- DT_INVEST
- ID_OCUPA_N
- DT_COPRO
- AN_QUANT
- OUTROS
- TRATANAO
- STCURA1
- STCURA2
- STCURA3
- TPAUTOCTO
- COPAISINF
- COMUNINF
- NOPROPIN
- NOCOLINF
- DT_ENCERRA
- DT_DIGITA
- DT_TRANSUS
- DT_TRANSDM
- DT_TRANSSM
- DT_TRANSRS
- DT_TRANSSE
- DT_OBITO
- DS_FORMA
- DTTRAT
- DT_RESU3
- OUTRO_EX

## Colunas adicionadas no processamento (3 colunas)

Presentes apenas no processado:
- IDADE_PROCESSADA
- delay_notificacao_dias
- tempo_encerramento_dias
