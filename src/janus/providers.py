"""Provedores de LLM para o Janus (OpenAI-compatível, Ollama local e Mock)."""

from __future__ import annotations

import abc
import json
import os
import urllib.error
import urllib.request
from typing import Any


class LLMProvider(abc.ABC):
    """Interface base para qualquer provedor de modelo de linguagem."""

    name: str = "base"

    @abc.abstractmethod
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Executa uma chamada ao modelo e retorna um dicionário JSON válido."""


def _extract_json(raw_text: str) -> dict[str, Any]:
    """Extrai e faz parse de JSON mesmo se vier envolvido por blocos markdown."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"Resposta do modelo não contém JSON válido: {raw_text[:200]}")


class OpenAICompatibleProvider(LLMProvider):
    """Provedor para APIs compatíveis com OpenAI (OpenAI, OpenRouter, Groq, DeepSeek)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.3,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("JANUS_MODEL", "gpt-4o-mini")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.temperature = temperature
        self.timeout = timeout
        self.name = f"openai:{self.model}"

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY não definida. Configure a variável de ambiente ou use --provider ollama/mock."
            )

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Erro HTTP {exc.code} ao chamar {url}: {detail}") from exc

        content = body["choices"][0]["message"]["content"]
        return _extract_json(content)


class OllamaProvider(LLMProvider):
    """Provedor local via Ollama (sem necessidade de API key)."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.3,
        timeout: int = 120,
    ) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.temperature = temperature
        self.timeout = timeout
        self.name = f"ollama:{self.model}"

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": self.temperature},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Não foi possível conectar ao Ollama em {self.base_url}. "
                "Verifique se o servidor Ollama está em execução."
            ) from exc

        content = body["message"]["content"]
        return _extract_json(content)


class MockProvider(LLMProvider):
    """Provedor determinístico offline para testes automatizados, CI e demonstrações."""

    name = "mock:deterministic"

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if "FASE 1" in user_prompt:
            return {
                "approaches": [
                    {
                        "id": "A1",
                        "name": "Evolução Incremental Controlada",
                        "strategy_type": "Conservadora",
                        "summary": (
                            "Executa melhorias em ciclos curtos sobre a estrutura atual, "
                            "validando métricas antes de expandir o escopo."
                        ),
                        "pros": [
                            "Baixo risco operacional e reversão imediata",
                            "Custo inicial reduzido e entregas rápidas",
                        ],
                        "cons": [
                            "Pode não eliminar gargalos estruturais profundos",
                            "Teto de escalabilidade menor no longo prazo",
                        ],
                        "assumptions": ["A base atual suporta extensões modulares"],
                    },
                    {
                        "id": "A2",
                        "name": "Arquitetura Híbrida Pragmática (Strangler Pattern)",
                        "strategy_type": "Equilibrada",
                        "summary": (
                            "Isola os componentes críticos em novos módulos desacoplados "
                            "enquanto mantém o núcleo estável em operação."
                        ),
                        "pros": [
                            "Equilibra alto impacto com risco controlado",
                            "Permite migração progressiva sem interromper o serviço",
                        ],
                        "cons": [
                            "Exige disciplina de contratos e observabilidade",
                            "Complexidade temporária por manter dois caminhos ativos",
                        ],
                        "assumptions": ["É possível definir fronteiras claras de domínio"],
                    },
                    {
                        "id": "A3",
                        "name": "Reconstrução Total Orientada ao Futuro",
                        "strategy_type": "Arrojada",
                        "summary": (
                            "Desenha uma nova solução do zero eliminando dívidas acumuladas "
                            "e adotando o estado da arte."
                        ),
                        "pros": [
                            "Máximo potencial de impacto e performance no longo prazo",
                            "Elimina limitações herdadas",
                        ],
                        "cons": [
                            "Alto custo, prazo longo e risco elevado de atraso",
                            "Demora para gerar valor mensurável",
                        ],
                        "assumptions": ["Orçamento e prazo têm folga para ciclo longo"],
                    },
                ]
            }

        if "FASE 2" in user_prompt:
            return {
                "evaluations": [
                    {
                        "approach_id": "A1",
                        "scores": {
                            "impact": 6.5,
                            "feasibility": 9.0,
                            "risk_control": 9.0,
                            "speed": 8.8,
                            "cost_efficiency": 8.5,
                        },
                        "rationales": {
                            "impact": "Resolve sintomas prioritários, mas limita ganhos estruturais.",
                            "feasibility": "Execução direta com recursos atuais.",
                            "risk_control": "Mudanças pequenas facilitam rollback.",
                            "speed": "Primeiras entregas na primeira semana.",
                            "cost_efficiency": "Baixo investimento necessário.",
                        },
                        "failure_modes": [
                            "Acúmulo de remendos dificultando evolução futura",
                            "Estagnação dos indicadores após ganhos iniciais",
                        ],
                    },
                    {
                        "approach_id": "A2",
                        "scores": {
                            "impact": 8.8,
                            "feasibility": 8.0,
                            "risk_control": 8.2,
                            "speed": 7.5,
                            "cost_efficiency": 7.8,
                        },
                        "rationales": {
                            "impact": "Ataca os principais gargalos com visão sustentável.",
                            "feasibility": "Viável com planejamento incremental por marcos.",
                            "risk_control": "Permite validar cada módulo isoladamente.",
                            "speed": "Entrega valor real já no primeiro módulo crítico.",
                            "cost_efficiency": "Investimento proporcional ao retorno obtido.",
                        },
                        "failure_modes": [
                            "Sincronização mal definida entre sistema legado e novo módulo",
                            "Escopo crescer antes de estabilizar o primeiro marco",
                        ],
                    },
                    {
                        "approach_id": "A3",
                        "scores": {
                            "impact": 9.4,
                            "feasibility": 4.2,
                            "risk_control": 3.2,
                            "speed": 3.5,
                            "cost_efficiency": 4.0,
                        },
                        "rationales": {
                            "impact": "Potencial máximo caso entregue integralmente.",
                            "feasibility": "Alta dependência de alinhamento e capacidade técnica.",
                            "risk_control": "Risco elevado de estouro de prazo e regressões.",
                            "speed": "Longo período sem entregas visíveis.",
                            "cost_efficiency": "Alto custo upfront com retorno tardio.",
                        },
                        "failure_modes": [
                            "Síndrome do segundo sistema e paralisia por escopo",
                            "Mudança de prioridades antes do lançamento",
                        ],
                    },
                ]
            }

        return {
            "decision_rationale": (
                "A Arquitetura Híbrida Pragmática (A2) oferece o melhor equilíbrio entre impacto "
                "estrutural e controle de risco. Enquanto a abordagem conservadora (A1) tem teto "
                "baixo de ganho e a reconstrução total (A3) expõe o projeto a risco inaceitável, "
                "A2 captura resultados consistentes com entregas fatiadas e reversíveis."
            ),
            "action_plan": [
                "Mapear o componente de maior gargalo e definir métricas de linha de base.",
                "Especificar contratos de entrada/saída e critérios objetivos de sucesso.",
                "Implementar o primeiro módulo isolado com telemetria e feature flag.",
                "Validar em ambiente real com tráfego/escopo controlado e medir impacto.",
                "Expandir progressivamente para os próximos módulos ou ajustar a rota.",
            ],
            "fallback_trigger": (
                "Se o primeiro módulo não demonstrar ganho mensurável ou ultrapassar 30% do "
                "esforço estimado na etapa piloto, congelar a expansão e adotar A1."
            ),
        }
