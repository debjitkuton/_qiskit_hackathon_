"""Tests for target platform profiles and payload management."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.problem import (
    load_platform,
    load_platforms,
    locate_payloads,
    Platform,
    PROCESSORS_DIR,
    PARAMETER_SETS,
    PAYLOAD_SIZES,
)


class TestPlatforms:
    @pytest.mark.parametrize("key", ["A", "B", "C", "D"])
    def test_load_single_platform(self, key: str):
        platform = load_platform(key)
        assert isinstance(platform, Platform)
        assert platform.key == key
        assert platform.name
        assert platform.role
        assert platform.status

    def test_load_all_platforms(self):
        platforms = load_platforms()
        assert set(platforms.keys()) == {"A", "B", "C", "D"}
        
        # Verify Platform B has 1 core
        assert platforms["B"].cpu_cores == 1
        assert platforms["B"].mem_budget_mb == 128
        
        # Verify Platform C has edge budget
        assert platforms["C"].cpu_cores == 1
        assert platforms["C"].mem_budget_mb == 8
        assert platforms["C"].chunk_bytes == 16 * 1024

        # Verify Platform D custom tuned record size
        assert platforms["D"].cpu_cores == 1
        assert platforms["D"].mem_budget_mb == 8
        assert platforms["D"].chunk_bytes == 64 * 1024

    def test_processors_json_files_exist(self):
        for key in ["A", "B"]:
            path = PROCESSORS_DIR / f"processor_{key}.json"
            assert path.exists(), f"Missing processor definition: {path}"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "coupling_map" in data

    def test_locate_payloads_standins(self):
        payloads = locate_payloads(generate_standins=True)
        assert "1KB" in payloads
        assert "100KB" in payloads
        assert "10MB" in payloads

        for label, nominal_size in PAYLOAD_SIZES.items():
            payload = payloads[label]
            assert payload.path.exists()
            assert payload.size == nominal_size

    def test_parameter_sets_consistency(self):
        for name, pset in PARAMETER_SETS.items():
            assert pset.name == name
            assert pset.kem
            assert pset.sig
            assert pset.kdf == "HKDF-SHA256"
            assert pset.aead == "AES-256-GCM"
            assert pset.describe()
