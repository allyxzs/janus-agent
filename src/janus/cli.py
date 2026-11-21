"""Interface de linha de comando (CLI) do agente Janus."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from janus.agent import JanusAgent
from janus.env import load_dotenv
from janus.formatters import format_report_markdown, format_report_text
from janus.models import PROFILES
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


def _format_profiles_text() -> str:
    lines = ["PERFIS DE DECISÃO DISPONÍVEIS:"]
    for name, criteria in PROFILES.items():
        lines.append(f"\n  [{name}]")
        for c in criteria:
            veto = f" (mín: {c.min_acceptable:.1f})" if c.min_acceptable is not None else ""
            lines.append(f"    - {c.label} ({c.name}): peso {c.weight:.0%}{veto}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="janus",
        description="Janus — Avalia possibilidades e define a melhor abordagem.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "profiles",
        help="Lista os perfis de critérios pré-configurados (pesos e regras de veto).",
    )

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
        "--profile",
        default="balanced",
        choices=sorted(PROFILES.keys()),
        help="Perfil de pesos e vetos (padrão: balanced).",
    )
    analyze_cmd.add_argument(
        "--approaches",
        type=int,
        default=3,
        help="Quantidade de possibilidades a gerar (2 a 6, padrão: 3).",
    )
    analyze_cmd.add_argument(
        "--provider",
        default=None,
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
    analyze_cmd.add_argument(
        "--markdown",
        action="store_true",
        dest="as_markdown",
        help="Exibe o relatório formatado em Markdown (ideal para ADRs e PRs).",
    )
    analyze_cmd.add_argument(
        "--output",
        default=None,
        help="Salva a saída em um arquivo (ex.: decisao.md ou decisao.json).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "profiles":
        print(_format_profiles_text())
        return 0

    if args.command == "analyze":
        provider_name = args.provider or os.getenv("JANUS_PROVIDER", "mock")
        try:
            provider = _build_provider(provider_name, args.model)
            agent = JanusAgent(provider=provider)
            report = agent.analyze(
                args.problem,
                goal=args.goal,
                constraints=args.constraint,
                profile=args.profile,
                num_approaches=args.approaches,
            )
        except Exception as exc:
            print(f"Erro ao executar Janus: {exc}", file=sys.stderr)
            return 1

        if args.as_json:
            rendered = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
        elif args.as_markdown:
            rendered = format_report_markdown(report)
        else:
            rendered = format_report_text(report)

        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
            print(f"Relatório salvo em: {args.output}")
        else:
            print(rendered)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
