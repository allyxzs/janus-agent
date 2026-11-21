"""Modelos de dados estruturados e perfis de decisão do agente Janus."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Criterion:
    """Critério usado para avaliar e pontuar cada abordagem possível.

    Attributes:
        name: Identificador curto do critério (ex.: 'impact', 'feasibility').
        label: Nome legível para exibição em relatórios.
        weight: Peso relativo do critério (normalizado automaticamente).
        description: O que uma nota alta (10) significa neste critério.
        min_acceptable: Nota mínima (0-10) abaixo da qual a abordagem sofre veto.
    """

    name: str
    label: str
    weight: float
    description: str = ""
    min_acceptable: float | None = None


DEFAULT_CRITERIA: list[Criterion] = [
    Criterion(
        name="impact",
        label="Impacto",
        weight=0.30,
        description="Capacidade da abordagem de resolver a raiz do problema e gerar valor.",
    ),
    Criterion(
        name="feasibility",
        label="Viabilidade",
        weight=0.25,
        description="Facilidade técnica e operacional de executar com os recursos atuais.",
        min_acceptable=4.0,
    ),
    Criterion(
        name="risk_control",
        label="Controle de Risco",
        weight=0.20,
        description="Segurança, previsibilidade e facilidade de reversão caso algo falhe.",
        min_acceptable=3.5,
    ),
    Criterion(
        name="speed",
        label="Velocidade",
        weight=0.15,
        description="Rapidez para entregar os primeiros resultados mensuráveis.",
    ),
    Criterion(
        name="cost_efficiency",
        label="Eficiência de Custo",
        weight=0.10,
        description="Relação entre custo/esforço investido e retorno obtido.",
    ),
]


PROFILES: dict[str, list[Criterion]] = {
    "balanced": DEFAULT_CRITERIA,
    "conservative": [
        Criterion(
            name="risk_control",
            label="Controle de Risco",
            weight=0.35,
            description="Segurança, previsibilidade e reversão imediata.",
            min_acceptable=6.5,
        ),
        Criterion(
            name="feasibility",
            label="Viabilidade",
            weight=0.25,
            description="Execução segura com o time e recursos atuais.",
            min_acceptable=6.0,
        ),
        Criterion(
            name="impact",
            label="Impacto",
            weight=0.20,
            description="Ganho consistente sem expor a operação.",
        ),
        Criterion(
            name="cost_efficiency",
            label="Eficiência de Custo",
            weight=0.10,
            description="Baixo comprometimento financeiro inicial.",
        ),
        Criterion(
            name="speed",
            label="Velocidade",
            weight=0.10,
            description="Entregas incrementais previsíveis.",
        ),
    ],
    "aggressive": [
        Criterion(
            name="impact",
            label="Impacto",
            weight=0.45,
            description="Transformação estrutural e máximo retorno potencial.",
        ),
        Criterion(
            name="speed",
            label="Velocidade",
            weight=0.25,
            description="Velocidade para capturar vantagem competitiva.",
        ),
        Criterion(
            name="feasibility",
            label="Viabilidade",
            weight=0.15,
            description="Capacidade técnica de entregar sob ambição alta.",
            min_acceptable=3.0,
        ),
        Criterion(
            name="risk_control",
            label="Controle de Risco",
            weight=0.10,
            description="Mitigação mínima para riscos críticos.",
            min_acceptable=2.5,
        ),
        Criterion(
            name="cost_efficiency",
            label="Eficiência de Custo",
            weight=0.05,
            description="Uso racional de recursos.",
        ),
    ],
    "frugal": [
        Criterion(
            name="cost_efficiency",
            label="Eficiência de Custo",
            weight=0.35,
            description="Máximo retorno com mínimo gasto e infraestrutura.",
            min_acceptable=6.0,
        ),
        Criterion(
            name="feasibility",
            label="Viabilidade",
            weight=0.25,
            description="Execução simples com equipe enxuta.",
            min_acceptable=5.5,
        ),
        Criterion(
            name="impact",
            label="Impacto",
            weight=0.20,
            description="Resolução objetiva do problema principal.",
        ),
        Criterion(
            name="speed",
            label="Velocidade",
            weight=0.10,
            description="Tempo curto até o primeiro resultado.",
        ),
        Criterion(
            name="risk_control",
            label="Controle de Risco",
            weight=0.10,
            description="Prevenção de retrabalho caro.",
            min_acceptable=4.0,
        ),
    ],
}


def get_profile_criteria(profile: str) -> list[Criterion]:
    """Retorna uma cópia da lista de critérios de um perfil pré-configurado."""
    key = profile.lower().strip()
    if key not in PROFILES:
        valid = ", ".join(sorted(PROFILES))
        raise ValueError(f"Perfil desconhecido: '{profile}'. Perfis válidos: {valid}.")
    return list(PROFILES[key])


@dataclass
class ProblemContext:
    """Contexto completo do problema a ser analisado pelo Janus."""

    problem: str
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    criteria: list[Criterion] = field(default_factory=lambda: list(DEFAULT_CRITERIA))
    num_approaches: int = 3


@dataclass
class Approach:
    """Uma possibilidade estratégica gerada na fase de divergência."""

    id: str
    name: str
    summary: str
    strategy_type: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Resultado da avaliação multicritério de uma abordagem."""

    approach: Approach
    scores: dict[str, float]
    rationales: dict[str, str]
    failure_modes: list[str]
    weighted_score: float = 0.0
    vetoed: bool = False
    veto_reasons: list[str] = field(default_factory=list)


@dataclass
class DecisionReport:
    """Relatório final produzido pelo Janus com a melhor abordagem e plano de ação."""

    problem: str
    goal: str
    recommended: EvaluationResult
    runner_up: EvaluationResult | None
    all_evaluations: list[EvaluationResult]
    criteria: list[Criterion]
    confidence: str
    sensitivity_note: str
    decision_rationale: str
    action_plan: list[str]
    fallback_trigger: str
    provider: str

    def to_dict(self) -> dict[str, Any]:
        """Converte o relatório completo para dicionário serializável em JSON."""
        return asdict(self)
