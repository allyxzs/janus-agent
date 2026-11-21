"""Testes unitários do motor determinístico de pontuação, veto e sensibilidade."""

import unittest

from janus.models import Approach, Criterion, EvaluationResult, get_profile_criteria
from janus.scoring import (
    compute_confidence,
    normalize_weights,
    rank_evaluations,
    sensitivity_check,
)


class TestScoring(unittest.TestCase):
    def test_normalize_weights_sums_to_one(self) -> None:
        criteria = [
            Criterion(name="a", label="A", weight=2.0),
            Criterion(name="b", label="B", weight=3.0),
        ]
        weights = normalize_weights(criteria)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)
        self.assertAlmostEqual(weights["a"], 0.4, places=6)
        self.assertAlmostEqual(weights["b"], 0.6, places=6)

    def test_veto_pushes_high_score_option_below_valid_option(self) -> None:
        criteria = [
            Criterion(name="impact", label="Impacto", weight=0.7),
            Criterion(name="risk", label="Risco", weight=0.3, min_acceptable=5.0),
        ]
        risky = EvaluationResult(
            approach=Approach(id="A1", name="Arriscada", summary="", strategy_type="Arrojada"),
            scores={"impact": 10.0, "risk": 2.0},
            rationales={},
            failure_modes=[],
        )
        safe = EvaluationResult(
            approach=Approach(id="A2", name="Segura", summary="", strategy_type="Equilibrada"),
            scores={"impact": 7.0, "risk": 8.0},
            rationales={},
            failure_modes=[],
        )

        ranked = rank_evaluations([risky, safe], criteria)
        self.assertEqual(ranked[0].approach.id, "A2")
        self.assertFalse(ranked[0].vetoed)
        self.assertEqual(ranked[1].approach.id, "A1")
        self.assertTrue(ranked[1].vetoed)
        self.assertEqual(compute_confidence(ranked), "alta")

    def test_sensitivity_detects_robust_leader(self) -> None:
        criteria = get_profile_criteria("balanced")
        strong = EvaluationResult(
            approach=Approach(id="A1", name="Forte", summary="", strategy_type="Equilibrada"),
            scores={
                "impact": 9.0,
                "feasibility": 8.5,
                "risk_control": 8.5,
                "speed": 8.0,
                "cost_efficiency": 8.0,
            },
            rationales={},
            failure_modes=[],
        )
        weak = EvaluationResult(
            approach=Approach(id="A2", name="Fraca", summary="", strategy_type="Conservadora"),
            scores={
                "impact": 6.0,
                "feasibility": 6.5,
                "risk_control": 6.0,
                "speed": 6.0,
                "cost_efficiency": 6.0,
            },
            rationales={},
            failure_modes=[],
        )
        ranked = rank_evaluations([strong, weak], criteria)
        note = sensitivity_check(ranked, criteria)
        self.assertIn("Robusta", note)


if __name__ == "__main__":
    unittest.main()
