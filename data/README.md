# Dados (data/)

Este arquivo descreve as colunas presentes nos arquivos de dados em data/ e quais foram removidas no processamento.

## Arquivos

- sinan_esqu_raw.parquet: dados brutos.
- processed/sinan_esqu_processed.parquet: dados processados.
- processed/sinan_esq_processed_with_dt_notific.parquet: dados processados com DT_NOTIFIC.


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
