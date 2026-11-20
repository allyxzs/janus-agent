"""Motor determinístico de pontuação multicritério e análise de margem."""

from __future__ import annotations

from janus.models import Criterion, EvaluationResult


def normalize_weights(criteria: list[Criterion]) -> dict[str, float]:
    """Normaliza os pesos dos critérios para que a soma seja igual a 1.0."""
    if not criteria:
        raise ValueError("É necessário fornecer ao menos um critério de avaliação.")

    total = sum(max(c.weight, 0.0) for c in criteria)
    if total <= 0:
        equal = 1.0 / len(criteria)
        return {c.name: equal for c in criteria}

    return {c.name: max(c.weight, 0.0) / total for c in criteria}


def clamp_score(value: float, low: float = 0.0, high: float = 10.0) -> float:
    """Garante que uma pontuação esteja dentro do intervalo [0, 10]."""
    return max(low, min(high, float(value)))


def score_evaluation(
    evaluation: EvaluationResult,
    criteria: list[Criterion],
) -> EvaluationResult:
    """Calcula a pontuação ponderada e verifica regras de veto."""
    weights = normalize_weights(criteria)
    weighted_sum = 0.0
    veto_reasons: list[str] = []

    for criterion in criteria:
        raw = evaluation.scores.get(criterion.name, 5.0)
        clamped = clamp_score(raw)
        evaluation.scores[criterion.name] = clamped
        weighted_sum += clamped * weights[criterion.name]

        if criterion.min_acceptable is not None and clamped < criterion.min_acceptable:
            veto_reasons.append(
                f"{criterion.label} abaixo do mínimo aceitável "
                f"({clamped:.1f} < {criterion.min_acceptable:.1f})"
            )

    evaluation.weighted_score = round(weighted_sum, 2)
    evaluation.vetoed = len(veto_reasons) > 0
    evaluation.veto_reasons = veto_reasons
    return evaluation


def rank_evaluations(
    evaluations: list[EvaluationResult],
    criteria: list[Criterion],
) -> list[EvaluationResult]:
    """Pontua e ordena abordagens priorizando opções sem veto e maior nota ponderada."""
    scored = [score_evaluation(ev, criteria) for ev in evaluations]
    return sorted(
        scored,
        key=lambda ev: (not ev.vetoed, ev.weighted_score),
        reverse=True,
    )


def compute_confidence(ranked: list[EvaluationResult]) -> str:
    """Define o nível de confiança com base na margem entre o 1º e o 2º colocado."""
    if not ranked:
        return "baixa"
    if ranked[0].vetoed:
        return "baixa (todas as opções sofreram veto — revisar restrições)"
    if len(ranked) == 1:
        return "alta"

    winner = ranked[0]
    runner_up = ranked[1]

    if runner_up.vetoed:
        return "alta"

    margin = winner.weighted_score - runner_up.weighted_score
    if margin >= 1.2:
        return "alta"
    if margin >= 0.5:
        return "média"
    return "moderada (empate técnico — considere validação rápida)"
