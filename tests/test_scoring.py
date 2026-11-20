"""Testes unitários do motor determinístico de pontuação e veto."""

import unittest

from janus.models import Approach, Criterion, EvaluationResult
from janus.scoring import compute_confidence, normalize_weights, rank_evaluations


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


if __name__ == "__main__":
    unittest.main()
