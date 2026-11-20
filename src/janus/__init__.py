"""Janus — Agente de avaliação estratégica e definição da melhor abordagem."""

from janus.agent import JanusAgent
from janus.models import (
    Approach,
    Criterion,
    DecisionReport,
    EvaluationResult,
    ProblemContext,
)
from janus.providers import (
    LLMProvider,
    MockProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
)

__all__ = [
    "JanusAgent",
    "Approach",
    "Criterion",
    "DecisionReport",
    "EvaluationResult",
    "ProblemContext",
    "LLMProvider",
    "MockProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
]

__version__ = "0.1.0"
