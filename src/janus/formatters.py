"""Formatadores de saída para relatórios do Janus (Texto e Markdown)."""

from __future__ import annotations

from janus.models import DecisionReport


def format_report_text(report: DecisionReport) -> str:
    """Formata o relatório de decisão para leitura clara no terminal."""
    lines: list[str] = []
    sep = "=" * 72
    lines.append(sep)
    lines.append("JANUS — RELATÓRIO DE DECISÃO ESTRATÉGICA")
    lines.append(sep)
    lines.append(f"Problema      : {report.problem}")
    if report.goal:
        lines.append(f"Objetivo      : {report.goal}")
    lines.append(f"Provedor      : {report.provider}")
    lines.append(f"Confiança     : {report.confidence}")
    lines.append(f"Sensibilidade : {report.sensitivity_note}")
    lines.append("")

    rec = report.recommended
    header = (
        f">>> MELHOR ABORDAGEM: [{rec.approach.id}] {rec.approach.name} "
        f"({rec.weighted_score:.2f}/10)"
    )
    lines.append(header)
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


def format_report_markdown(report: DecisionReport) -> str:
    """Formata o relatório em Markdown pronto para ADRs, PRs e documentação."""
    rec = report.recommended
    lines: list[str] = [
        "# Janus — Relatório de Decisão Estratégica",
        "",
        f"- **Problema:** {report.problem}",
    ]
    if report.goal:
        lines.append(f"- **Objetivo:** {report.goal}")
    lines.extend(
        [
            f"- **Provedor:** `{report.provider}`",
            f"- **Confiança:** {report.confidence}",
            f"- **Sensibilidade:** {report.sensitivity_note}",
            "",
            f"## Melhor Abordagem: [{rec.approach.id}] {rec.approach.name}",
            "",
            f"> **Nota ponderada:** `{rec.weighted_score:.2f}/10` · "
            f"**Perfil:** {rec.approach.strategy_type}",
            "",
            rec.approach.summary,
            "",
            "### Justificativa",
            "",
            report.decision_rationale,
            "",
            "## Matriz Comparativa",
            "",
        ]
    )

    crit_headers = [c.label for c in report.criteria]
    header_row = "| Pos | Abordagem | " + " | ".join(crit_headers) + " | Nota | Status |"
    sep_row = "| :-: | :--- | " + " | ".join([":-:"] * len(crit_headers)) + " | :-: | :---: |"
    lines.append(header_row)
    lines.append(sep_row)

    for pos, ev in enumerate(report.all_evaluations, start=1):
        scores_str = " | ".join(
            f"{ev.scores.get(c.name, 0.0):.1f}" for c in report.criteria
        )
        status = "VETO" if ev.vetoed else "Aprovada"
        lines.append(
            f"| {pos} | **[{ev.approach.id}]** {ev.approach.name} | "
            f"{scores_str} | **{ev.weighted_score:.2f}** | {status} |"
        )

    lines.extend(["", "## Plano de Ação", ""])
    for step in report.action_plan:
        lines.append(f"- [ ] {step}")

    lines.extend(
        [
            "",
            "## Gatilho de Contingência (Plano B)",
            "",
            f"> {report.fallback_trigger}",
            "",
        ]
    )
    return "\n".join(lines)
