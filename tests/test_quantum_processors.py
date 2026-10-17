"""Tests for quantum processor topologies, routing analysis, and Qiskit probes."""
from __future__ import annotations

import pytest

from src.architecture_probe import ghz5_circuit, run_probe
from src.routing import (
    build_graph,
    graph_metrics,
    load_processor,
    processor_graph_table,
    swap_lower_bound,
    to_qiskit_coupling_map,
    validate,
)


class TestQuantumTopologies:
    @pytest.mark.parametrize("key", ["A", "B", "D"])
    def test_processor_definitions_valid(self, key: str):
        probs = validate(key)
        assert probs == [], f"Validation errors for Processor {key}: {probs}"

    def test_processor_qubit_counts(self):
        assert load_processor("A")["num_qubits"] == 5
        assert load_processor("B")["num_qubits"] == 9
        assert load_processor("D")["num_qubits"] == 9

    def test_graph_metrics(self):
        proc_a = load_processor("A")
        g_a = build_graph(proc_a["coupling_map"], proc_a["num_qubits"])
        metrics_a = graph_metrics(g_a)
        assert metrics_a["qubits"] == 5
        assert metrics_a["diameter"] == 4  # 5-qubit chain has diameter 4

        proc_d = load_processor("D")
        g_d = build_graph(proc_d["coupling_map"], proc_d["num_qubits"])
        metrics_d = graph_metrics(g_d)
        assert metrics_d["qubits"] == 9
        assert metrics_d["max_degree"] == 4
        assert metrics_d["avg_shortest_path"] <= metrics_a["avg_shortest_path"]

    def test_processor_graph_table(self):
        df = processor_graph_table()
        assert len(df) >= 3
        assert "qubits" in df.columns
        assert "diameter" in df.columns


class TestQiskitProbes:
    def test_ghz5_circuit_structure(self):
        qc = ghz5_circuit()
        assert qc.num_qubits == 5
        assert qc.num_clbits == 5
        assert qc.name == "STAR-GHZ-5"

    def test_to_qiskit_coupling_map(self):
        cmap_a = to_qiskit_coupling_map("A")
        assert cmap_a.size() == 5
        cmap_b = to_qiskit_coupling_map("B")
        assert cmap_b.size() == 9

    def test_run_probe_results_and_zero_swaps_on_d(self):
        rows = run_probe(shots=4096)
        assert len(rows) == 3

        row_a = [r for r in rows if r["processor"] == "A"][0]
        row_b = [r for r in rows if r["processor"] == "B"][0]
        row_d = [r for r in rows if r["processor"] == "D"][0]

        assert row_a["p_success_ideal"] == 1.0
        assert row_b["p_success_ideal"] == 1.0
        assert row_d["p_success_ideal"] == 1.0

        # Processor D (3x3 grid) achieves 0 SWAPs due to planar connectivity
        assert row_d["swap_count"] == 0
        assert row_a["swap_count"] > row_d["swap_count"]
