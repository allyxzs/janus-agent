# Janus Agent

> **Janus** é um agente de IA focado em decisão estratégica: ele explora múltiplas possibilidades, avalia trade-offs com matriz multicritério determinística e define a melhor abordagem com plano de ação e gatilho de contingência.

Inspirado no deus romano das transições e escolhas — que olha simultaneamente para o passado (contexto e restrições) e para o futuro (riscos e desdobramentos) — o **Janus** evita respostas impulsivas dividindo o raciocínio em três etapas explícitas.

---

## Arquitetura de Decisão

```text
Problema + Restrições
        │
        ▼
┌──────────────────────────────┐
│ 1. EXPLORER (Divergência)    │  Gera abordagens distintas (Conservadora, Equilibrada, Arrojada)
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 2. EVALUATOR (Análise)       │  Pontua critérios (0-10) + análise Pre-Mortem (modos de falha)
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 3. SCORING ENGINE (Código)   │  Ponderação determinística + regras de veto + nível de confiança
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ 4. ARBITER (Síntese)         │  Justificativa + Plano de Ação + Gatilho de Contingência (Plano B)
└──────────────────────────────┘
```

## Principais Recursos

- **Zero dependências externas no core**: roda usando apenas a biblioteca padrão do Python 3.10+.
- **Provedor agnóstico**: compatível com **OpenAI** (e APIs compatíveis como OpenRouter, Groq e DeepSeek), **Ollama** (modelos locais) e **Mock** (offline/CI).
- **Motor de decisão auditável**: a pontuação ponderada e os vetos por risco mínimo são calculados em Python determinístico, não apenas "no chute" do LLM.
- **CLI e SDK Python**: use diretamente pelo terminal ou integre em seus pipelines e sistemas multiagente.

---

## Instalação

```bash
git clone https://github.com/SEU_USUARIO/janus-agent.git
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

Teste offline imediatamente usando o provedor `mock`:

```bash
janus analyze "Migrar monólito para microsserviços sem downtime"   --goal "Reduzir tempo de deploy em 60%"   --constraint "Equipe de 4 pessoas"   --provider mock
```

Usando **OpenAI** (com `OPENAI_API_KEY` configurada):

```bash
janus analyze "Definir arquitetura de cache para API de alta carga"   --provider openai   --model gpt-4o-mini
```

Usando **Ollama** localmente:

```bash
janus analyze "Escolher stack para aplicativo mobile multiplataforma"   --provider ollama   --model llama3.1
```

Saída estruturada em JSON (ideal para automações e integração com outros agentes):

```bash
janus analyze "Expandir produto para mercado internacional" --provider mock --json
```

### Via Python SDK

```python
from janus import JanusAgent, OpenAICompatibleProvider

agent = JanusAgent(provider=OpenAICompatibleProvider(model="gpt-4o-mini"))

report = agent.analyze(
    problem="Nosso banco de dados principal está atingindo 90% de CPU nos horários de pico.",
    goal="Estabilizar latência p95 abaixo de 150ms em 60 dias.",
    constraints=["Sem janela de manutenção longa", "Orçamento limitado"],
)

print("Melhor abordagem:", report.recommended.approach.name)
print("Nota:", report.recommended.weighted_score)
print("Confiança:", report.confidence)
print("Plano de ação:", report.action_plan)
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
│   ├── models.py         # Dataclasses e critérios padrão
│   ├── prompts.py        # Prompts estruturados das 3 fases
│   ├── providers.py      # OpenAI-compatível, Ollama e Mock
│   └── scoring.py        # Matriz ponderada determinística e regras de veto
├── tests/
│   ├── test_agent.py
│   └── test_scoring.py
├── .env.example
├── .gitignore
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
pytest -v
```

---

## Publicando no GitHub

```bash
git init
git add .
git commit -m "feat: initial release of Janus decision agent"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/janus-agent.git
git push -u origin main
```

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
