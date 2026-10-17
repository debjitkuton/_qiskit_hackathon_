"""Tests for Man-in-the-Middle (MITM) attack scenarios and adversary defense."""
from __future__ import annotations

import pytest

from src.process import get_backend, mitm_scenarios


class TestMITMDefense:
    @pytest.mark.parametrize("param_set", ["classical-p256", "pqc-L3", "hybrid-L3"])
    def test_all_mitm_scenarios_pass(self, param_set: str):
        backend = get_backend(param_set)
        rows = mitm_scenarios(backend)
        assert len(rows) == 7

        control_row = [r for r in rows if r["scenario"] == "no attacker (control)"][0]
        assert control_row["pass"] is True
        assert control_row["payload_delivered_intact"] is True

        attack_rows = [r for r in rows if r["scenario"] != "no attacker (control)"]
        for attack in attack_rows:
            assert attack["pass"] is True, f"Failed defense for: {attack['scenario']}"
            assert attack["attack_detected"] is True, f"Attack not detected: {attack['scenario']}"
            assert attack["payload_delivered_intact"] is False, f"Tampered payload was delivered: {attack['scenario']}"

    @pytest.mark.parametrize("scenario_idx", range(7))
    def test_pqc_l3_individual_mitm_scenario(self, scenario_idx: int):
        backend = get_backend("pqc-L3")
        rows = mitm_scenarios(backend)
        row = rows[scenario_idx]
        assert row["pass"] is True, f"Failed scenario: {row['scenario']} (details: {row['detail']})"
