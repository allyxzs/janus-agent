"""Testes de integração do pipeline completo do JanusAgent, CLI e .env."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from janus import JanusAgent, MockProvider, load_dotenv
from janus.cli import main as cli_main
from janus.providers import _extract_json


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
        self.assertTrue(bool(report.sensitivity_note))

    def test_conservative_profile_prefers_incremental_option(self) -> None:
        agent = JanusAgent(provider=MockProvider())
        report = agent.analyze(
            problem="Atualizar módulo financeiro crítico.",
            profile="conservative",
        )
        self.assertEqual(report.recommended.approach.id, "A1")

    def test_empty_problem_raises_value_error(self) -> None:
        agent = JanusAgent(provider=MockProvider())
        with self.assertRaises(ValueError):
            agent.analyze("   ")

    def test_cli_json_and_markdown_output(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_main(
                ["analyze", "Reduzir custos de nuvem", "--provider", "mock", "--json"]
            )
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["recommended"]["approach"]["id"], "A2")

        md_buf = io.StringIO()
        with redirect_stdout(md_buf):
            code_md = cli_main(
                ["analyze", "Reduzir custos de nuvem", "--provider", "mock", "--markdown"]
            )
        self.assertEqual(code_md, 0)
        self.assertIn("## Matriz Comparativa", md_buf.getvalue())

    def test_cli_output_file_and_profiles_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "decisao.md"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_main(
                    [
                        "analyze",
                        "Escolher banco de dados",
                        "--provider",
                        "mock",
                        "--markdown",
                        "--output",
                        str(out_path),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue(out_path.is_file())
            self.assertIn("# Janus", out_path.read_text(encoding="utf-8"))

        prof_buf = io.StringIO()
        with redirect_stdout(prof_buf):
            code_prof = cli_main(["profiles"])
        self.assertEqual(code_prof, 0)
        self.assertIn("[conservative]", prof_buf.getvalue())

    def test_extract_json_handles_markdown_fences(self) -> None:
        raw = '```json\n{"ok": true, "score": 9.5}\n```'
        parsed = _extract_json(raw)
        self.assertEqual(parsed["ok"], True)
        self.assertEqual(parsed["score"], 9.5)

    def test_load_dotenv_reads_variables(self) -> None:
        key = "JANUS_TEST_DOTENV_KEY"
        os.environ.pop(key, None)
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(f'# comment\n{key}="valor_teste"\n', encoding="utf-8")
            loaded = load_dotenv(env_file)
            self.assertTrue(loaded)
            self.assertEqual(os.environ.get(key), "valor_teste")
        os.environ.pop(key, None)


if __name__ == "__main__":
    unittest.main()
