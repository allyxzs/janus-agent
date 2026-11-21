# Contribuindo com o Janus

Contribuições são muito bem-vindas! Este guia descreve como preparar seu ambiente e enviar melhorias.

## Setup local

```bash
git clone https://github.com/allyxzs/janus-agent.git
cd janus-agent
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Qualidade e Testes

Antes de abrir um Pull Request, garanta que os testes e o linter passem sem erros:

```bash
ruff check src tests examples
pytest -v
```

## Fluxo de Pull Request

1. Crie uma branch descritiva (`feat/novo-provedor`, `fix/ajuste-veto`).
2. Escreva testes cobrindo suas alterações.
3. Mantenha commits claros e objetivos.
4. Abra o Pull Request explicando o contexto e o impacto da mudança.
