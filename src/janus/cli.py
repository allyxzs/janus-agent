"""Interface de linha de comando (CLI) do agente Janus."""

from __future__ import annotations

import argparse
import json
import os
import sys

from janus.agent import JanusAgent
from janus.models import DecisionReport
from janus.providers import (
    LLMProvider,
    MockProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
)


def _build_provider(name: str, model: str | None) -> LLMProvider:
    provider_name = name.lower().strip()
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "ollama":
        return OllamaProvider(model=model)
    if provider_name == "openai":
        return OpenAICompatibleProvider(model=model)
    raise ValueError(f"Provedor desconhecido: '{name}'. Use openai, ollama ou mock.")


def format_report_text(report: DecisionReport) -> str:
    """Formata o relatório de decisão para leitura clara no terminal."""
    lines: list[str] = []
    sep = "=" * 72
    lines.append(sep)
    lines.append("JANUS — RELATÓRIO DE DECISÃO ESTRATÉGICA")
    lines.append(sep)
    lines.append(f"Problema  : {report.problem}")
    if report.goal:
        lines.append(f"Objetivo  : {report.goal}")
    lines.append(f"Provedor  : {report.provider}")
    lines.append(f"Confiança : {report.confidence}")
    lines.append("")

    rec = report.recommended
    lines.append(f">>> MELHOR ABORDAGEM: [{rec.approach.id}] {rec.approach.name} ({rec.weighted_score:.2f}/10)")
    lines.append(f"    Tipo: {rec.approach.strategy_type}")
    lines.append(f"    Resumo: {rec.approach.summary}")
    lines.append("")

    lines.append("JUSTIFICATIVA DA DECISÃO:")
    lines.append(f"  {report.decision_rationale}")
    lines.append("")

    lines.append("RANKING DE POSSIBILIDADES:")
    for pos, ev in enumerate(report.all_evaluations, start=1):
        status = " [VETO]" if ev.vetoed else ""
        lines.append(
            f"  {pos}. [{ev.approach.id}] {ev.approach.name} — {ev.weighted_score:.2f}/10{status}"
        )
        if ev.veto_reasons:
            for reason in ev.veto_reasons:
                lines.append(f"       ! Motivo de veto: {reason}")
    lines.append("")

    lines.append("PLANO DE AÇÃO:")
    for idx, step in enumerate(report.action_plan, start=1):
        lines.append(f"  {idx}. {step}")
    lines.append("")

    lines.append("GATILHO DE CONTINGÊNCIA (PLANO B):")
    lines.append(f"  {report.fallback_trigger}")
    lines.append(sep)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="janus",
        description="Janus — Avalia possibilidades e define a melhor abordagem.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_cmd = sub.add_parser(
        "analyze",
        help="Analisa um problema, avalia abordagens e recomenda a melhor estratégia.",
    )
    analyze_cmd.add_argument("problem", help="Descrição do problema ou decisão a tomar.")
    analyze_cmd.add_argument("--goal", default="", help="Objetivo principal esperado.")
    analyze_cmd.add_argument(
        "--constraint",
        action="append",
        default=[],
        help="Restrição a considerar (pode ser usada múltiplas vezes).",
    )
    analyze_cmd.add_argument(
        "--approaches",
        type=int,
        default=3,
        help="Quantidade de possibilidades a gerar (2 a 6, padrão: 3).",
    )
    analyze_cmd.add_argument(
        "--provider",
        default=os.getenv("JANUS_PROVIDER", "mock"),
        choices=["openai", "ollama", "mock"],
        help="Provedor de LLM (padrão: JANUS_PROVIDER ou 'mock').",
    )
    analyze_cmd.add_argument(
        "--model",
        default=None,
        help="Nome do modelo a utilizar no provedor selecionado.",
    )
    analyze_cmd.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Exibe o relatório completo em formato JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        try:
            provider = _build_provider(args.provider, args.model)
            agent = JanusAgent(provider=provider)
            report = agent.analyze(
                args.problem,
                goal=args.goal,
                constraints=args.constraint,
                num_approaches=args.approaches,
            )
        except Exception as exc:
            print(f"Erro ao executar Janus: {exc}", file=sys.stderr)
            return 1

        if args.as_json:
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_report_text(report))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
