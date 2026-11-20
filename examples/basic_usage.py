"""Exemplo básico de uso do Janus via Python SDK."""

from janus import JanusAgent, MockProvider
from janus.cli import format_report_text


def main() -> None:
    # Troque MockProvider() por OpenAICompatibleProvider() ou OllamaProvider() em produção
    agent = JanusAgent(provider=MockProvider())

    report = agent.analyze(
        problem="Nossa API monolítica está atingindo gargalos de latência em horários de pico.",
        goal="Reduzir latência p95 em 50% nos próximos 90 dias sem downtime.",
        constraints=[
            "Equipe enxuta de 3 engenheiros",
            "Orçamento de nuvem não pode crescer mais que 20%",
        ],
    )

    print(format_report_text(report))


if __name__ == "__main__":
    main()
