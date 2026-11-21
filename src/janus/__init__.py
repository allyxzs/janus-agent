"""Janus — Agente de avaliação estratégica e definição da melhor abordagem."""

from janus.agent import JanusAgent
from janus.env import load_dotenv
from janus.models import (
    DEFAULT_CRITERIA,
    PROFILES,
    Approach,
    Criterion,
    DecisionReport,
    EvaluationResult,
    ProblemContext,
    get_profile_criteria,
)
from janus.providers import (
    LLMProvider,
    MockProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
)

__all__ = [
    "Approach",
    "Criterion",
    "DEFAULT_CRITERIA",
    "DecisionReport",
    "EvaluationResult",
    "JanusAgent",
    "LLMProvider",
    "MockProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "PROFILES",
    "ProblemContext",
    "get_profile_criteria",
    "load_dotenv",
]

__version__ = "0.2.0"
