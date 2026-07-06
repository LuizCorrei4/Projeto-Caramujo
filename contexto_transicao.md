# Contexto de Transição - Projeto Caramujo (Handover)

Olá, Ítalo (e respectivo agente LLM auxiliador)! 

Este documento foi elaborado para facilitar o seu embarque imediato no desenvolvimento do **Projeto Caramujo**. O projeto é um Sistema de Vigilância Socioambiental cujo objetivo é identificar e prever polos de risco epidemiológico para a **Esquistossomose**, cruzando dados de notificação médica (SINAN), infraestrutura sanitária (SNIS), monitoramento hídrico por satélite (MapBiomas) e censos (IBGE).

---

## 1. O que já foi desenvolvido (O Aplicativo Streamlit)

Nós consolidamos os achados dos notebooks originais em uma aplicação interativa de múltiplas páginas utilizando **Streamlit**. O aplicativo já está funcional e se encontra no diretório `streamlit_app/`. 

A estrutura é a seguinte:
- `streamlit_app/app.py`: Página inicial de contextualização institucional do sistema.
- `streamlit_app/pages/1_Painel_Epidemiologico.py`: Dashboard de análise descritiva com dados do SINAN. (Nota técnica: os dicionários numéricos de Raça, Escolaridade e UF já foram traduzidos semanticamente no próprio código para exibição limpa nos gráficos).
- `streamlit_app/pages/2_Mapeamento_e_Perfis.py`: Página dedicada a exibir graficamente o **Paradoxo do Saneamento** (a falta de correlação linear isolada entre saneamento e incidência) e a explicar com clareza os 5 Perfis de Risco identificados matematicamente pelo algoritmo K-Means.
- `streamlit_app/pages/3_Simulador_de_Risco.py`: Interface de Inteligência Artificial. Utiliza um algoritmo de *Random Forest* (treinado dinamicamente na base de municípios ativos) para simular o risco de um cenário ambiental se tornar um epicentro da doença.
- `streamlit_app/utils/`: Contém os motores por trás do app (`data_loader.py` com alto uso de cache de memória, e `model_trainer.py` que treina as árvores de decisão *on-the-fly* aplicando *Undersampling*).

---

## 2. Leitura Obrigatória para o Agente LLM

Para que você (Agente IA do Ítalo) consiga refinar os modelos, adicionar lógicas ou solucionar bugs, **é imperativo** que você utilize suas ferramentas de leitura de arquivo para inspecionar os seguintes documentos de arquitetura que já deixamos prontos:

1. `contexto/contexto_repositorio.md`: **A Bíblia do Projeto.** Detalha como as variáveis do MapBiomas foram transformadas (a lógica por trás da variável `açudes_canais_ha`), o fluxo do K-Means e do Random Forest, e as escolhas de mitigação de desbalanceamento.
2. `contexto/plano_aplicacao_streamlit.md`: O planejamento estrutural arquitetônico do Streamlit.
3. `anotacoes/dicionario.md`: Contém a chave de decodificação das variáveis brutas da base do SINAN.
4. (Opcional para aprofundamento): `notebooks/analise_geoespacial/analise_saneamento_corpos_d'agua.ipynb`.

---

## 3. Como Rodar o Sistema Localmente

As bibliotecas necessárias (`streamlit`, `plotly`, `scikit-learn`, `fastparquet`, `pyarrow`) já foram instaladas no ambiente virtual atual. Para rodar a versão atualizada da aplicação, o Ítalo deve abrir o terminal na raiz do repositório (`/home/gabyl/projetos/Projeto-Caramujo`) e executar:

```bash
streamlit run streamlit_app/app.py
```

---

## 4. Próximos Passos e Desafios para Refinamento

1. **Deploy no Streamlit Community Cloud (Atenção aos Dados):** O principal desafio imediato para publicar o dashboard é que os arquivos `.parquet` processados em `data/processed/` (necessários para a aplicação rodar) atualmente estão ignorados pelo `.gitignore`. O Ítalo precisará decidir se forçará a subida desses dados específicos para o GitHub (`git add -f`) ou se vai configurar um download por URL no `data_loader.py`.
2. **Refinamento Visual do Mapa:** A página 2 utiliza `plotly.express.scatter_mapbox`. No futuro, pode-se avaliar o uso de polígonos reais dos municípios (via GeoJSON/geopandas ou Pydeck), caso a performance do servidor suporte.
3. **Novos Filtros:** Adicionar seletores mais granulares (ex: filtrar o mapa por faixas específicas de saneamento).

Bom trabalho na continuidade deste sistema preventivo de saúde pública!
