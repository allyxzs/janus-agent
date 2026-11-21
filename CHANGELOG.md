# Changelog

Todas as alterações relevantes do **Janus Agent** serão documentadas neste arquivo.

## [0.2.0] - 2026-11-21

### Adicionado
- Perfis de decisão pré-configurados: `balanced`, `conservative`, `aggressive` e `frugal`.
- Novo subcomando `janus profiles` para inspecionar pesos e regras de veto no terminal.
- Exportação em Markdown (`--markdown`) com tabela comparativa e checklist de ações.
- Opção `--output` na CLI para salvar relatórios diretamente em disco.
- Análise automática de sensibilidade (`sensitivity_check`) no motor de pontuação.
- Carregamento automático de arquivo `.env` sem dependências externas (`janus.env.load_dotenv`).
- Retry com backoff exponencial em falhas transitórias de rede/HTTP nos provedores LLM.

### Corrigido
- Conformidade com PEP 639 no `pyproject.toml` (`setuptools>=77.0`, `license = "MIT"`), corrigindo falhas de build no GitHub Actions.
- Adicionado `fail-fast: false` e Python 3.13 na matriz do workflow de CI.
- Padronização de todas as linhas e ordenação de imports para passar integralmente no `ruff check` (`E`, `F`, `I`, `W`).
- Conversão resiliente de pontuações retornadas como string pelo LLM (`_safe_float`).

## [0.1.0] - 2026-11-20

### Adicionado
- Release inicial com pipeline `Explorar -> Avaliar -> Decidir`, motor determinístico de pontuação/veto, CLI e provedores `OpenAICompatibleProvider`, `OllamaProvider` e `MockProvider`.
