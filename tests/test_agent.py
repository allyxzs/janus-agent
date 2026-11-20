"""Testes de integração do pipeline completo do JanusAgent e da CLI."""

import io
import json
import unittest
from contextlib import redirect_stdout

from janus import JanusAgent, MockProvider
from janus.cli import main as cli_main


class TestJanusAgent(unittest.TestCase):
    def test_janus_pipeline_selects_best_non_vetoed_approach(self) -> None:
        agent = JanusAgent(provider=MockProvider())
        report = agent.analyze(
            problem="Migrar sistema legado sem interromper operação.",
            goal="Reduzir incidentes em 40%",
            constraints=["Sem downtime"],
        )

        self.assertEqual(report.recommended.approach.id, "A2")
        self.assertFalse(report.recommended.vetoed)
        self.assertEqual(len(report.all_evaluations), 3)
        vetoed_ids = [ev.approach.id for ev in report.all_evaluations if ev.vetoed]
        self.assertIn("A3", vetoed_ids)
        self.assertGreaterEqual(len(report.action_plan), 3)
        self.assertTrue(bool(report.fallback_trigger))

    def test_empty_problem_raises_value_error(self) -> None:
        agent = JanusAgent(provider=MockProvider())
        with self.assertRaises(ValueError):
            agent.analyze("   ")

    def test_cli_json_output(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = cli_main(
                ["analyze", "Reduzir custos de infraestrutura", "--provider", "mock", "--json"]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["recommended"]["approach"]["id"], "A2")
        self.assertEqual(payload["provider"], "mock:deterministic")


if __name__ == "__main__":
    unittest.main()
