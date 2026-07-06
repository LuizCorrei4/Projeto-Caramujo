# Plano de Implementação da Aplicação Streamlit: Sistema de Vigilância Socioambiental para Esquistossomose

Este documento detalha o planejamento arquitetural, a estrutura de interface e a lógica de processamento de dados para a construção da aplicação Streamlit do Projeto Caramujo. O objetivo é criar uma ferramenta intuitiva para gestores públicos e pesquisadores, traduzindo modelos analíticos complexos em visualizações acessíveis e acionáveis.

A linguagem da aplicação será formal, técnica, porém de fácil compreensão, abstendo-se do uso de elementos informais (como emojis) para garantir credibilidade institucional.

---

## 1. Arquitetura do Software e Estrutura de Diretórios

A aplicação utilizará o recurso de múltiplas páginas (Multipage App) do Streamlit para organizar as análises de forma lógica e evitar a sobrecarga de informações em uma única tela.

**Estrutura Proposta:**
```text
streamlit_app/
│
├── app.py                         # Ponto de entrada (Página Inicial/Apresentação)
├── pages/
│   ├── 1_Painel_Epidemiologico.py # Análise descritiva (Casos e Demografia)
│   ├── 2_Mapeamento_e_Perfis.py   # Mapas e relação Saneamento vs Hidrografia (Clusters)
│   └── 3_Simulador_de_Risco.py    # Preditor de Machine Learning interativo
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py             # Funções de carregamento com @st.cache_data
│   └── model_trainer.py           # Lógica de treinamento on-the-fly do Random Forest
│
└── requirements.txt               # Dependências específicas da interface
```

---

## 2. Estratégia de Processamento e Carregamento de Dados

Para garantir que a aplicação seja responsiva e fluida, a estratégia de manipulação de dados será:

1. **Uso de Cache Eficiente:** Todas as funções no módulo `data_loader.py` utilizarão o decorador `@st.cache_data`. Isso garante que as bases pesadas (como os arquivos `.parquet` consolidados) sejam lidas para a memória apenas uma vez durante a inicialização do servidor.
2. **Separação de Contextos:**
   - Dados clínicos brutos (SINAN) serão usados primariamente na Página 1.
   - Dados tratados agregados (`dados_tratados_2015_2019.csv` e `2020_2025.csv`) serão a espinha dorsal das Páginas 2 e 3, pois já contêm as variáveis socioambientais e os rótulos de cluster.
3. **Treinamento do Modelo em Tempo de Execução (On-the-fly):** Como a base de municípios ativos consolidada é pequena (menos de 600 registros), o modelo preditivo (Random Forest) e a padronização (StandardScaler) serão treinados dinamicamente na inicialização do `Simulador_de_Risco.py`, armazenando o modelo treinado em `@st.cache_resource`. Isso elimina a necessidade de gerenciar arquivos de modelo serializados (arquivos `.pkl`).

---

## 3. Estrutura e Lógica das Páginas da Aplicação

### Página Inicial: `app.py`
- **Objetivo:** Receber o usuário e contextualizar o propósito da ferramenta.
- **Conteúdo:** 
  - Título formal: "Sistema de Inteligência Socioambiental para Prevenção da Esquistossomose".
  - Breve explicação sobre a doença e a premissa fundamental do projeto: a interseção entre falta de saneamento adequado e a presença de coleções hídricas antrópicas (pequenos açudes e canais).
  - Um guia rápido descrevendo o que o usuário encontrará nas páginas seguintes.

### Página 1: Painel Epidemiológico (Monitoramento Clínico)
- **Objetivo:** Apresentar a situação histórica e demográfica baseada exclusivamente em dados do SINAN.
- **Lógica e Componentes:**
  - Painel de filtros laterais (Barra Lateral): Seleção de Ano Inicial, Ano Final e Estado (UF).
  - Cartões de Métricas (KPIs): Total de casos confirmados, Idade Média, e Proporção de Cura.
  - Gráficos de Linha: Evolução temporal do número de casos.
  - Gráficos de Barras/Setor: Distribuição por sexo, raça e escolaridade.
- **Técnica Visual:** Utilização do `plotly.express` para garantir interatividade (zoom e dicas de contexto ao passar o mouse).

### Página 2: Mapeamento Espacial e Perfis de Vulnerabilidade
- **Objetivo:** Exibir a distribuição geográfica e explicar os perfis de risco (K-Means) descobertos na pesquisa.
- **Lógica e Componentes:**
  - **Mapa Georreferenciado:** Utilizando `plotly.express.scatter_mapbox` com os centroides dos municípios (`latitude` e `longitude`). O tamanho do marcador representará a incidência e a cor representará o nível de vulnerabilidade (Cluster).
  - **O Paradoxo do Saneamento:** Uma seção de texto analítico explicando que altas taxas de saneamento nominal não impedem focos da doença se houver alta concentração hídrica antrópica.
  - **Gráfico de Dispersão:** Taxa de Esgoto (Eixo X) vs Incidência Logarítmica (Eixo Y), separada por cores dos perfis identificados.

### Página 3: Simulador de Risco Preditivo (Machine Learning)
- **Objetivo:** Permitir que gestores públicos avaliem o risco de um município com base em projeções estruturais, sem depender de notificações passadas de casos.
- **Lógica e Componentes:**
  - **Painel de Controle de Cenários:** O usuário utilizará controles deslizantes numéricos para definir características hipotéticas ou reais de um município:
    - População estimada.
    - Taxa de coleta de esgoto (0% a 100%).
    - Área de açudes e canais (hectares).
    - Área de hidrografia natural (hectares).
    - Área de grandes represas (hectares).
  - **Motor Preditivo:** O Random Forest processará os valores inseridos.
  - **Saída do Simulador:** 
    - Um alerta claro de classificação: "Perfil de Baixo Risco Epidemiológico" ou "Perfil de Alto Risco Epidemiológico".
    - **Transparência do Algoritmo:** Exibição da importância percentual dos fatores na tomada de decisão do modelo (ex: "A área de açudes contribuiu com 30% para esta classificação").

---

## 4. Padrões de Design e Identidade Visual

- **Paleta de Cores:** Cores institucionais e profissionais. Tons de azul e cinza para estruturas base, com vermelho escuro ou laranja estritamente reservados para destacar municípios ou indicadores de alto risco.
- **Tipografia e Textos:** O uso de marcadores (bullets) será priorizado em detrimento de parágrafos longos. Textos descritivos não conterão gírias, emojis ou jargões médicos não explicados.
- **Layout Responsivo:** Configuração do Streamlit com `layout="wide"` para otimizar o uso da tela, organizando gráficos lado a lado utilizando `st.columns`.

---

## Próximos Passos (Fase de Execução)

Caso este plano seja aprovado, o desenvolvimento ocorrerá na seguinte ordem:
1. Criação do arcabouço de diretórios e do arquivo `app.py`.
2. Implementação das rotinas de extração em `utils/data_loader.py` e adaptação do script de treinamento dinâmico em `utils/model_trainer.py`.
3. Construção sequencial das interfaces visuais (Página 1, Página 2 e Página 3).
4. Revisão técnica de consistência dos dados exibidos contra os achados originais dos notebooks.
