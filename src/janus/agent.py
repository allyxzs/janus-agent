"""Núcleo de orquestração do agente Janus (Explorar -> Avaliar -> Decidir)."""

from __future__ import annotations

from typing import Any

from janus.models import (
    DEFAULT_CRITERIA,
    Approach,
    Criterion,
    DecisionReport,
    EvaluationResult,
    ProblemContext,
    get_profile_criteria,
)
from janus.prompts import (
    SYSTEM_PROMPT,
    build_decide_prompt,
    build_evaluate_prompt,
    build_explore_prompt,
)
from janus.providers import LLMProvider, MockProvider
from janus.scoring import compute_confidence, rank_evaluations, sensitivity_check


def _safe_float(value: Any, default: float = 5.0) -> float:
    """Converte valores numéricos retornados pelo LLM de forma resiliente."""
    if value is None or isinstance(value, bool):
        return default
    try:
        return float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


class JanusAgent:
    """Agente que explora possibilidades, avalia trade-offs e define a melhor abordagem."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider: LLMProvider = provider or MockProvider()

    def analyze(
        self,
        problem: str,
        *,
        goal: str = "",
        constraints: list[str] | None = None,
        criteria: list[Criterion] | None = None,
        profile: str | None = None,
        num_approaches: int = 3,
    ) -> DecisionReport:
        """Executa o pipeline completo do Janus para um problema informado."""
        if not problem or not problem.strip():
            raise ValueError("O campo 'problem' não pode estar vazio.")

        if criteria is not None:
            resolved_criteria = list(criteria)
        elif profile is not None:
            resolved_criteria = get_profile_criteria(profile)
        else:
            resolved_criteria = list(DEFAULT_CRITERIA)

        ctx = ProblemContext(
            problem=problem.strip(),
            goal=goal.strip(),
            constraints=list(constraints or []),
            criteria=resolved_criteria,
            num_approaches=max(2, min(num_approaches, 6)),
        )

        # Fase 1: Divergência (geração de possibilidades)
        approaches = self._explore(ctx)

        # Fase 2: Convergência analítica (avaliação multicritério + pre-mortem)
        raw_evaluations = self._evaluate(ctx, approaches)

        # Motor determinístico de pontuação, veto e sensibilidade
        ranked = rank_evaluations(raw_evaluations, ctx.criteria)
        confidence = compute_confidence(ranked)
        sensitivity = sensitivity_check(ranked, ctx.criteria)

        # Fase 3: Síntese, plano de ação e gatilho de contingência
        synthesis = self._decide(ctx, ranked)

        return DecisionReport(
            problem=ctx.problem,
            goal=ctx.goal,
            recommended=ranked[0],
            runner_up=ranked[1] if len(ranked) > 1 else None,
            all_evaluations=ranked,
            criteria=ctx.criteria,
            confidence=confidence,
            sensitivity_note=sensitivity,
            decision_rationale=synthesis["decision_rationale"],
            action_plan=synthesis["action_plan"],
            fallback_trigger=synthesis["fallback_trigger"],
            provider=self.provider.name,
        )

    def _explore(self, ctx: ProblemContext) -> list[Approach]:
        prompt = build_explore_prompt(ctx)
        data = self.provider.complete_json(SYSTEM_PROMPT, prompt)
        items = data.get("approaches", [])
        if not items:
            raise RuntimeError("O provedor não retornou nenhuma abordagem na Fase 1.")

        approaches: list[Approach] = []
        for idx, item in enumerate(items, start=1):
            approaches.append(
                Approach(
                    id=str(item.get("id", f"A{idx}")),
                    name=str(item.get("name", f"Abordagem {idx}")),
                    strategy_type=str(item.get("strategy_type", "Estratégica")),
                    summary=str(item.get("summary", "")),
                    pros=[str(p) for p in item.get("pros", [])],
                    cons=[str(c) for c in item.get("cons", [])],
                    assumptions=[str(a) for a in item.get("assumptions", [])],
                )
            )
        return approaches

    def _evaluate(
        self,
        ctx: ProblemContext,
        approaches: list[Approach],
    ) -> list[EvaluationResult]:
        prompt = build_evaluate_prompt(ctx, approaches, ctx.criteria)
        data = self.provider.complete_json(SYSTEM_PROMPT, prompt)
        raw_map = {
            str(item.get("approach_id")): item for item in data.get("evaluations", [])
        }

        results: list[EvaluationResult] = []
        for approach in approaches:
            item = raw_map.get(approach.id, {})
            scores = {
                str(k): _safe_float(v) for k, v in (item.get("scores") or {}).items()
            }
            rationales = {
                str(k): str(v) for k, v in (item.get("rationales") or {}).items()
            }
            failure_modes = [str(f) for f in item.get("failure_modes", [])]

            results.append(
                EvaluationResult(
                    approach=approach,
                    scores=scores,
                    rationales=rationales,
                    failure_modes=failure_modes,
                )
            )
        return results

    def _decide(
        self,
        ctx: ProblemContext,
        ranked: list[EvaluationResult],
    ) -> dict[str, Any]:
        prompt = build_decide_prompt(ctx, ranked)
        data = self.provider.complete_json(SYSTEM_PROMPT, prompt)
        return {
            "decision_rationale": str(data.get("decision_rationale", "")),
            "action_plan": [str(step) for step in data.get("action_plan", [])],
            "fallback_trigger": str(data.get("fallback_trigger", "")),
        }
