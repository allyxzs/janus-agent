"""Exemplo de personalização de critérios, pesos e regras de veto."""

from janus import Criterion, JanusAgent, MockProvider


def main() -> None:
    custom_criteria = [
        Criterion(
            name="risk_control",
            label="Segurança e Conformidade",
            weight=0.45,
            description="Aderência regulatória e baixo risco de incidentes.",
            min_acceptable=7.0,
        ),
        Criterion(
            name="impact",
            label="Impacto no Negócio",
            weight=0.35,
            description="Capacidade de resolver a dor central do cliente.",
        ),
        Criterion(
            name="speed",
            label="Time-to-Market",
            weight=0.20,
            description="Velocidade de lançamento.",
        ),
    ]

    agent = JanusAgent(provider=MockProvider())
    report = agent.analyze(
        problem="Escolher estratégia de autenticação para plataforma financeira.",
        criteria=custom_criteria,
    )

    print(f"Recomendação: {report.recommended.approach.name}")
    print(f"Pontuação ponderada: {report.recommended.weighted_score}/10")
    print(f"Confiança: {report.confidence}")


if __name__ == "__main__":
    main()
