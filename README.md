# Projeto Caramujo - Esquistossomose

Analise exploratoria e preprocessamento de dados de esquistossomose, com notebooks e dados auxiliares.

## Estrutura

- `notebooks/`: notebooks de AED e preprocessamento.
- `data/`: dados locais (apenas `sinan_esqu_raw.parquet` e versionado).
- `anotacoes/`: dicionario de dados e notas.
- `images/`: imagens geradas para relatorios ou notebooks.

## Dados

Somente `data/sinan_esqu_raw.parquet` deve ser versionado. Os demais arquivos em `data/` sao considerados locais.

Se algum arquivo de `data/` ja estiver no Git, remova-o do indice antes de publicar:

```bash
git rm --cached data/arquivo_que_nao_deve_subir
```

## Como executar

Requisitos: Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Abra os notebooks em `notebooks/` a partir do Jupyter.

## Notebooks

- `AED_Esquistossomose_Final.ipynb`: analise exploratoria final.
- `eixo1_esqu.ipynb`: exploracoes do eixo 1.
- `esqu_preprocess_FINAL.ipynb`: preprocessamento dos dados.

## Documentacao

- `anotacoes/dicionario.md`: dicionario de variaveis e codigos.

## Licenca

MIT. Veja `LICENSE`.
