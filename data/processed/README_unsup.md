# Detalhes do dataset SINAN ESQU - perfil não supervisionado

## Visão geral

Este documento descreve o arquivo `data/processed/sinan_esqu_unsup.parquet`, usado na etapa de análise e modelagem não supervisionada. O arquivo atual tem 135.084 registros e 19 colunas.

Regras principais do perfil:

- mantém todas as evoluções do caso;
- remove apenas registros com `AN_QUALI = 2`;
- preserva `EVOLUCAO`, `AN_QUALI`, `DT_NOTIFIC` e `SG_UF_NOT` no artefato atual;
- não usa `EVOLUCAO` como alvo;
- produz variáveis derivadas de idade e tempo de processamento;
- a base padrão atual mantém `DT_NOTIFIC` para leitura temporal e geográfica.

Para a lista completa das colunas originais do SINAN e das colunas descartadas no processamento bruto, consultar o dicionário em `anotacoes/dicionario.md`.

## Colunas finais do parquet

| Coluna | Descrição | Observação |
| --- | --- | --- |
| `ID_AGRAVO` | Agravo registrado. | No arquivo atual é constante em `B659`. |
| `DT_NOTIFIC` | Data de notificação. | Mantida para leitura temporal e cálculo das features derivadas. |
| `SG_UF_NOT` | UF de notificação. | Variável geográfica do registro. |
| `ID_MUNICIP` | Município de notificação. | Identificador geográfico/notificador. |
| `ID_UNIDADE` | Unidade notificadora. | Identificador da unidade de saúde ou serviço. |
| `CS_SEXO` | Sexo do paciente. | Variável demográfica. |
| `CS_GESTANT` | Situação gestacional. | Variável demográfica. |
| `CS_RACA` | Raça/cor. | Variável demográfica e social. |
| `CS_ESCOL_N` | Escolaridade. | Variável demográfica e social. |
| `SG_UF` | UF de residência. | Variável geográfica. |
| `TRATAM` | Informação sobre tratamento realizado. | Variável assistencial. |
| `FORMA` | Forma clínica/anátomo-clínica. | Variável clínica. |
| `COUFINF` | UF da provável fonte de infecção. | Variável epidemiológica/geográfica. |
| `DOENCA_TRA` | Relação com o trabalho. | Variável epidemiológica. |
| `EVOLUCAO` | Evolução do caso. | Usar como leitura pós-cluster. |
| `AN_QUALI` | Resultado do exame Hoffman. | Usar como leitura pós-cluster. |
| `IDADE_PROCESSADA` | Idade convertida para anos no momento do evento. | Criada no processamento. |
| `delay_notificacao_dias` | Dias entre início dos sintomas e notificação. | Feature temporal. |
| `tempo_encerramento_dias` | Dias entre notificação e encerramento. | Feature temporal. |

## Notas de processamento

- `IDADE_PROCESSADA` é gerada no step de limpeza e normalização da idade.
- `delay_notificacao_dias` e `tempo_encerramento_dias` são geradas no feature engineering.
- `DT_NOTIFIC` e `SG_UF_NOT` permanecem no parquet atual para apoiar leituras temporais e geográficas.
- Campos vazios e códigos ignorados são padronizados antes da imputação.
- `EVOLUCAO` e `AN_QUALI` ficam fora da imputação no perfil não supervisionado.

## Leituras analíticas possíveis

Esta base é adequada para explorar:

- perfis latentes de casos;
- grupos com atraso maior de notificação ou encerramento;
- diferenças entre perfis clínicos e sociodemográficos;
- padrões de registro incompletos ou inconsistentes;
- casos atípicos que podem indicar erro de preenchimento ou comportamento raro;
- semelhanças entre municípios, unidades ou regiões de residência.

## Referências do pipeline

- Perfil não supervisionado: `src/pipeline/config.py`
- Seleção da coorte: `src/pipeline/run_pipeline.py`
- Idade processada: `src/pipeline/steps/02_clean_and_impute.py`
- Features temporais: `src/pipeline/steps/03_feature_engineering.py`
- Artefatos e colunas finais: `data/README_data.md`