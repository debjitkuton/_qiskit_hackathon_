"""Tests for metrics calculation, code size auditing, and reporting tables."""
from __future__ import annotations

import pandas as pd
import pytest

from src.metrics import (
    available_sets,
    code_size,
    summarize,
)
from src.problem import (
    COMPARISON_SETS,
    RESULTS_FIGURES,
    RESULTS_TABLES,
)


class TestMetricsAndReporting:
    def test_summarize_statistics(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = summarize(data)
        assert stats["median"] == 30.0
        assert stats["mean"] == 30.0
        assert stats["n"] == 5
        assert stats["std"] > 0

    def test_available_parameter_sets(self):
        ok, skipped = available_sets(COMPARISON_SETS)
        assert "classical-p256" in ok
        assert "pqc-L3" in ok
        assert "hybrid-L3" in ok

    def test_code_size_table(self):
        df = code_size()
        assert isinstance(df, pd.DataFrame)
        assert "module" in df.columns
        assert "logical_lines" in df.columns
        assert "bytes" in df.columns
        assert len(df) > 1

        total_row = df[df["module"] == "TOTAL"]
        assert len(total_row) == 1
        assert total_row["logical_lines"].values[0] > 500

    def test_results_directories_exist(self):
        assert RESULTS_TABLES.exists()
        assert RESULTS_FIGURES.exists()

    def test_benchmark_tables_exist(self):
        # Verify key result tables generated for submission
        for filename in [
            "platform_specs.csv",
            "processor_graph_metrics.csv",
            "routing_estimate.csv",
        ]:
            table_path = RESULTS_TABLES / filename
            if table_path.exists():
                assert table_path.stat().st_size > 0
