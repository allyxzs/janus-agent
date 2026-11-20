"""Prompts estruturados para as 3 fases cognitivas do Janus."""

from __future__ import annotations

import json
from janus.models import Approach, Criterion, EvaluationResult, ProblemContext

SYSTEM_PROMPT = """Você é Janus, um agente especialista em decisão estratégica e arquitetura de soluções.
Assim como o deus romano de duas faces, você analisa simultaneamente o contexto/restrições atuais
e os desdobramentos futuros de cada escolha.

Regras obrigatórias:
1. Seja objetivo, analítico e concreto — evite generalidades vazias.
2. Responda EXCLUSIVAMENTE em JSON válido, sem blocos de markdown ou texto extra fora do JSON.
3. Escreva todo o conteúdo textual em português do Brasil, salvo termos técnicos consolidados.
"""


def build_explore_prompt(ctx: ProblemContext) -> str:
    constraints_text = "\n".join(f"- {c}" for c in ctx.constraints) or "- Nenhuma restrição explícita."
    return f"""FASE 1 — EXPLORAÇÃO DE POSSIBILIDADES

Problema: {ctx.problem}
Objetivo: {ctx.goal or "Definir a melhor estratégia geral para resolver o problema."}
Restrições:
{constraints_text}

Gere exatamente {ctx.num_approaches} abordagens REALMENTE DISTINTAS entre si (por exemplo: uma incremental/conservadora, uma equilibrada/pragmática e uma arrojada/estrutural).

Retorne um JSON exatamente neste formato:
{{
  "approaches": [
    {{
      "id": "A1",
      "name": "Nome curto da abordagem",
      "strategy_type": "Conservadora | Equilibrada | Arrojada",
      "summary": "Descrição objetiva de como funciona em 2-3 frases.",
      "pros": ["Vantagem concreta 1", "Vantagem concreta 2"],
      "cons": ["Desvantagem ou custo 1", "Desvantagem ou custo 2"],
      "assumptions": ["Premissa crítica que precisa ser verdadeira"]
    }}
  ]
}}
"""


def build_evaluate_prompt(
    ctx: ProblemContext,
    approaches: list[Approach],
    criteria: list[Criterion],
) -> str:
    criteria_spec = [
        {
            "name": c.name,
            "label": c.label,
            "weight": c.weight,
            "description": c.description,
        }
        for c in criteria
    ]
    approaches_spec = [
        {
            "id": a.id,
            "name": a.name,
            "strategy_type": a.strategy_type,
            "summary": a.summary,
            "pros": a.pros,
            "cons": a.cons,
        }
        for a in approaches
    ]
    return f"""FASE 2 — AVALIAÇÃO MULTICRITÉRIO E PRE-MORTEM

Problema: {ctx.problem}
Objetivo: {ctx.goal or "Resolver o problema com a melhor relação risco/retorno."}

Critérios (dê notas de 0.0 a 10.0, onde 10.0 é excelente):
{json.dumps(criteria_spec, ensure_ascii=False, indent=2)}

Abordagens para avaliar:
{json.dumps(approaches_spec, ensure_ascii=False, indent=2)}

Avalie cada abordagem de forma rigorosa e diferenciada (evite dar notas iguais para tudo).
Inclua também 2 modos de falha concretos (pre-mortem) para cada abordagem.

Retorne um JSON exatamente neste formato:
{{
  "evaluations": [
    {{
      "approach_id": "A1",
      "scores": {{
        "<criterion_name>": 7.5
      }},
      "rationales": {{
        "<criterion_name>": "Justificativa curta e objetiva"
      }},
      "failure_modes": ["Como isso pode falhar na prática 1", "Modo de falha 2"]
    }}
  ]
}}
"""


def build_decide_prompt(
    ctx: ProblemContext,
    ranked: list[EvaluationResult],
) -> str:
    summary = [
        {
            "id": ev.approach.id,
            "name": ev.approach.name,
            "weighted_score": ev.weighted_score,
            "vetoed": ev.vetoed,
            "veto_reasons": ev.veto_reasons,
            "scores": ev.scores,
            "failure_modes": ev.failure_modes,
        }
        for ev in ranked
    ]
    winner = ranked[0]
    return f"""FASE 3 — SÍNTESE E DEFINIÇÃO DA MELHOR ABORDAGEM

Problema: {ctx.problem}
Abordagem vencedora pelo motor de decisão: {winner.approach.name} (ID: {winner.approach.id}, Nota: {winner.weighted_score}/10)

Ranking completo:
{json.dumps(summary, ensure_ascii=False, indent=2)}

Explique por que a abordagem vencedora supera as demais, crie um plano de ação prático em 4 a 5 passos
e defina um gatilho claro de contingência (quando pivotar para o plano B).

Retorne um JSON exatamente neste formato:
{{
  "decision_rationale": "Síntese direta explicando os trade-offs e por que esta é a melhor escolha.",
  "action_plan": [
    "Passo 1 concreto",
    "Passo 2 concreto",
    "Passo 3 concreto",
    "Passo 4 concreto"
  ],
  "fallback_trigger": "Condição mensurável que indica que devemos migrar para a segunda opção."
}}
"""
