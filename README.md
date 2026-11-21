# Janus Agent

[![CI](https://github.com/allyxzs/janus-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/allyxzs/janus-agent/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Janus** é um agente de IA focado em decisão estratégica: ele explora múltiplas possibilidades, avalia trade-offs com matriz multicritério determinística, testa a sensibilidade da escolha e define a melhor abordagem com plano de ação e gatilho de contingência.

Inspirado no deus romano das transições e escolhas — que olha simultaneamente para o passado (contexto e restrições) e para o futuro (riscos e desdobramentos) — o **Janus** evita respostas impulsivas dividindo o raciocínio em etapas auditáveis.

---

## Arquitetura de Decisão

```text
Problema + Restrições + Perfil
             │
             ▼
┌────────────────────────────────────┐
│ 1. EXPLORER (Divergência)          │  Gera abordagens distintas (Conservadora, Equilibrada, Arrojada)
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│ 2. EVALUATOR (Análise)             │  Pontua critérios (0-10) + Pre-Mortem (modos de falha)
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│ 3. SCORING ENGINE (Determinístico) │  Ponderação + regras de veto + confiança + sensibilidade
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│ 4. ARBITER (Síntese)               │  Justificativa + Plano de Ação + Gatilho de Contingência
└────────────────────────────────────┘
```

## Principais Recursos

- **Zero dependências externas no core**: roda usando apenas a biblioteca padrão do Python 3.10+ (incluindo leitura automática de `.env`).
- **Provedor agnóstico com retry automático**: compatível com **OpenAI** (OpenAI, OpenRouter, Groq, DeepSeek), **Ollama** (local) e **Mock** (offline/CI).
- **Perfis de decisão prontos**: alterne entre `balanced`, `conservative`, `aggressive` e `frugal` ou passe seus próprios critérios.
- **Motor auditável com teste de sensibilidade**: pontuação ponderada, vetos por nota mínima e verificação automática de estabilidade da liderança.
- **Múltiplos formatos de saída**: terminal formatado, JSON estruturado (`--json`) e Markdown pronto para ADRs/PRs (`--markdown`), com opção de salvar em arquivo (`--output`).

---

## Instalação

```bash
git clone https://github.com/allyxzs/janus-agent.git
cd janus-agent
pip install -e .
```

Configure suas credenciais (opcional se usar `ollama` ou `mock`):

```bash
cp .env.example .env
```

---

## Uso rápido

### Via CLI

Listar os perfis de decisão disponíveis:

```bash
janus profiles
```

Rodar análise offline (`mock`) e exportar em Markdown para um arquivo:

```bash
janus analyze "Migrar monólito para microsserviços sem downtime" \
  --goal "Reduzir tempo de deploy em 60%" \
  --constraint "Equipe de 4 pessoas" \
  --profile conservative \
  --provider mock \
  --markdown \
  --output decisao.md
```

Usando **OpenAI** (com `OPENAI_API_KEY` no `.env` ou ambiente):

```bash
janus analyze "Definir arquitetura de cache para API de alta carga" \
  --provider openai \
  --model gpt-4o-mini
```

Usando **Ollama** localmente:

```bash
janus analyze "Escolher stack para aplicativo mobile multiplataforma" \
  --provider ollama \
  --model llama3.1
```

### Via Python SDK

```python
from janus import JanusAgent, OpenAICompatibleProvider

agent = JanusAgent(provider=OpenAICompatibleProvider(model="gpt-4o-mini"))

report = agent.analyze(
    problem="Nosso banco de dados principal está atingindo 90% de CPU nos horários de pico.",
    goal="Estabilizar latência p95 abaixo de 150ms em 60 dias.",
    constraints=["Sem janela de manutenção longa", "Orçamento limitado"],
    profile="balanced",
)

print("Melhor abordagem:", report.recommended.approach.name)
print("Nota:", report.recommended.weighted_score)
print("Confiança:", report.confidence)
print("Sensibilidade:", report.sensitivity_note)
```

---

## Estrutura do Projeto

```text
janus-agent/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/ci.yml
├── examples/
│   ├── basic_usage.py
│   └── custom_criteria.py
├── src/janus/
│   ├── __init__.py
│   ├── agent.py          # Orquestração Explorar -> Avaliar -> Decidir
│   ├── cli.py            # Interface de linha de comando
│   ├── env.py            # Carregador leve de .env sem dependências
│   ├── formatters.py     # Saída em texto formatado e Markdown
│   ├── models.py         # Dataclasses, critérios padrão e perfis
│   ├── prompts.py        # Prompts estruturados das 3 fases
│   ├── providers.py      # OpenAI-compatível, Ollama e Mock com retry
│   └── scoring.py        # Matriz ponderada, vetos e sensibilidade
├── tests/
│   ├── test_agent.py
│   └── test_scoring.py
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## Executando os Testes

```bash
pip install -e ".[dev]"
ruff check src tests examples
pytest -v
```

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
