"""Processor coupling maps and routing-cost metrics (Phase 1 architecture artifact).

The PS-P1 channel is classical: Track 5 target Platforms A/B/C/D are computing environments,
not quantum processors, and the PQC handshake is not run on quantum circuits. This module keeps
the separate Phase 1 Processor A/B architecture artifacts and optional routing/Qiskit analysis
aligned with the final Challenge Kit:

  * build the Processor A and B coupling maps themselves from the kit specification,
  * use the fixed A/B topologies in the required benchmark,
  * report SWAP / routing overhead.

Maps below follow the Challenge Kit (sections 3.1-3.3), which is the authoritative source.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pandas as pd

from .problem import PROCESSORS_DIR

# Kit specification, transcribed independently of the JSON files so they can be cross-checked.
CANDIDATE_TOPOLOGIES = {
    "A": {
        "reference_2016": {
            "name": "Processor A (5-qubit 2016-inspired reference)",
            "coupling_map": [(0, 1), (1, 2), (2, 3), (1, 4)],
            "topology": "2016-inspired five-node reference graph",
            "description": "2016-inspired five-qubit reference topology with synthetic noise model; diameter 3, average path length 1.8.",
        },
        "chain_baseline": {
            "name": "Processor A chain (optional candidate)",
            "coupling_map": [(0, 1), (1, 2), (2, 3), (3, 4)],
            "topology": "nearest-neighbor chain",
            "description": "5-qubit nearest-neighbor linear chain, edges 0-1-2-3-4.",
        },
        "ring": {
            "name": "Processor A ring (optional candidate)",
            "coupling_map": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
            "topology": "periodic 5-qubit ring",
            "description": "5-qubit ring with periodic boundary. Reduces diameter to 2 and average distance to 1.5, cutting SWAPs while maintaining uniform degree 2.",
        },
        "star": {
            "name": "Processor A (Star)",
            "coupling_map": [(0, 1), (0, 2), (0, 3), (0, 4)],
            "topology": "star graph",
            "description": "5-qubit star centered at q0. Fast 1-hop routing to hub, but hub degree 4 introduces frequency crowding and physical crosstalk.",
        },
    },
    "B": {
        "mesh_baseline": {
            "name": "Processor B (9-qubit mesh-loop topology)",
            "coupling_map": [
                (0, 1), (0, 8), (1, 2), (1, 6), (2, 3), (2, 5), (2, 6),
                (3, 4), (4, 5), (5, 6), (6, 7), (6, 8),
            ],
            "topology": "9-qubit chorded mesh graph",
            "description": "Processor B: 9-qubit topology with 12 edges, diameter 4, average shortest path 1.944.",
        },
        "tree_sparse": {
            "name": "Processor B sparse tree (optional candidate)",
            "coupling_map": [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 6), (4, 7), (7, 8)],
            "topology": "heavy-hex-inspired sparse graph",
            "description": "9-qubit heavy-hex-inspired sparse graph with branch points at 2 and 4.",
        },
        "grid_3x3": {
            "name": "Processor B 3x3 grid (optional candidate)",
            "coupling_map": [
                (0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8),
                (0, 3), (3, 6), (1, 4), (4, 7), (2, 5), (5, 8),
            ],
            "topology": "3x3 planar nearest-neighbor grid",
            "description": "9-qubit 2D mesh grid. Planar layout, diameter 4, average path length 2.0, multi-path routing with max degree 4.",
        },
        "ring_chord": {
            "name": "Processor B (Ring with Chords)",
            "coupling_map": [(i, (i + 1) % 9) for i in range(9)] + [(0, 4), (2, 7)],
            "topology": "9-qubit chorded ring",
            "description": "9-qubit ring augmented with 2 cross-links; diameter 3, average path length 1.917.",
        },
    },
}

KIT_COUPLING = {
    "A": CANDIDATE_TOPOLOGIES["A"]["reference_2016"]["coupling_map"],
    "B": CANDIDATE_TOPOLOGIES["B"]["mesh_baseline"]["coupling_map"],
    "D": CANDIDATE_TOPOLOGIES["B"]["grid_3x3"]["coupling_map"],
}
KIT_QUBITS = {"A": 5, "B": 9, "D": 9}

# Processor C is STUDY/REFERENCE ONLY (13 qubits): 12-node ring + centre qubit 12. Not required.
PROCESSOR_C_STUDY = [(i, (i + 1) % 12) for i in range(12)] + [(12, k) for k in (0, 2, 4, 6, 8, 10)]


PROCESSOR_D_SPEC = {
    "name": "Processor D (Candidate 9Q 3x3 Grid)",
    "source": "Physical 2D nearest-neighbor superconducting planar architecture",
    "num_qubits": 9,
    "topology": "2D 3x3 nearest-neighbor grid (planar square lattice)",
    "coupling_map": [
        [0, 1], [1, 2], [3, 4], [4, 5], [6, 7], [7, 8],
        [0, 3], [3, 6], [1, 4], [4, 7], [2, 5], [5, 8]
    ],
    "bidirectional": True,
    "basis_gates": ["rz", "sx", "x", "cx"],
    "noise": {
        "type": "challenge_defined",
        "source": "Challenge Kit section 3.4",
        "single_qubit_depolarizing": 0.001,
        "cx_depolarizing": 0.005,
        "readout_bitflip": 0.01
    },
    "benchmark": {
        "shots": 4096,
        "transpile_optimization_level": 1,
        "layout_routing": "SABRE",
        "seed": 42
    },
    "note": "Candidate architecture: 3x3 planar square grid. Maximum degree 4, diameter 4, 12 nearest-neighbor couplers. Designed to minimize SWAP routing overhead."
}


def load_processor(key: str) -> dict:
    p = Path(PROCESSORS_DIR) / f"processor_{key}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    if key == "D":
        return PROCESSOR_D_SPEC
    raise FileNotFoundError(f"Processor file not found: {p}")


def build_graph(edges, n_qubits: int) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(n_qubits))
    g.add_edges_from(tuple(e) for e in edges)  # CX is bidirectional in the kit
    return g


def validate(key: str) -> list[str]:
    """Validate a required Processor A/B file against the final Challenge Kit.

    Candidate maps may be analyzed separately, but the required processor files must match the
    published qubit count and undirected edge set exactly.
    """
    proc = load_processor(key)
    probs = []
    if proc.get("num_qubits") != KIT_QUBITS[key]:
        probs.append(f"{key}: expected {KIT_QUBITS[key]} qubits, JSON has {proc.get('num_qubits')}")
    cm = proc.get("coupling_map", [])
    if not cm:
        probs.append(f"{key}: coupling_map is empty")
        return probs
    for u, v in cm:
        if u == v or not (0 <= u < proc["num_qubits"] and 0 <= v < proc["num_qubits"]):
            probs.append(f"{key}: invalid edge ({u}, {v})")
    g = build_graph(cm, proc["num_qubits"])
    if not nx.is_connected(g):
        probs.append(f"{key}: coupling graph is not connected")
    expected_edges = {tuple(sorted(edge)) for edge in KIT_COUPLING[key]}
    actual_edges = {tuple(sorted(edge)) for edge in cm}
    if len(actual_edges) != len(cm):
        probs.append(f"{key}: coupling_map contains duplicate edges")
    if actual_edges != expected_edges:
        missing = sorted(expected_edges - actual_edges)
        extra = sorted(actual_edges - expected_edges)
        probs.append(f"{key}: coupling map must match the final Challenge Kit; missing={missing}, extra={extra}")
    return probs


def swap_lower_bound(g: nx.Graph, a: int, b: int) -> int:
    """Minimum SWAPs to make a CX between physical qubits a and b executable: distance - 1."""
    return max(0, nx.shortest_path_length(g, a, b) - 1)


def graph_metrics(g: nx.Graph) -> dict:
    n = g.number_of_nodes()
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    swaps = [swap_lower_bound(g, a, b) for a, b in pairs]
    return {
        "qubits": n, "edges": g.number_of_edges(), "max_degree": max(d for _, d in g.degree()),
        "avg_degree": round(2 * g.number_of_edges() / n, 3), "diameter": nx.diameter(g),
        "avg_shortest_path": round(nx.average_shortest_path_length(g), 3),
        "avg_swap_lower_bound_all_pairs": round(sum(swaps) / len(swaps), 3), "max_swap_lower_bound": max(swaps),
        "fully_connected_pairs_pct": round(100 * g.number_of_edges() / len(pairs), 1),
    }


def processor_graph_table() -> pd.DataFrame:
    rows = []
    for key in ("A", "B"):
        proc = load_processor(key)
        rows.append({"processor": proc["name"], "required": True, **graph_metrics(build_graph(proc["coupling_map"], proc["num_qubits"]))})
    # Optional topology analysis is separate from the required benchmark maps.
    for t_key, t_info in CANDIDATE_TOPOLOGIES["A"].items():
        if t_key == "reference_2016":
            continue
        rows.append({"processor": f"Candidate A: {t_info['name']}", "required": False, **graph_metrics(build_graph(t_info["coupling_map"], 5))})
    for t_key, t_info in CANDIDATE_TOPOLOGIES["B"].items():
        if t_key == "mesh_baseline":
            continue
        rows.append({"processor": f"Candidate B: {t_info['name']}", "required": False, **graph_metrics(build_graph(t_info["coupling_map"], 9))})
    rows.append({"processor": "Processor C (study only)", "required": False, **graph_metrics(build_graph(PROCESSOR_C_STUDY, 13))})
    # Processor D — team-designed supplemental topology for comparative analysis
    proc_d = load_processor("D")
    rows.append({"processor": proc_d["name"], "required": False,
                 **graph_metrics(build_graph(proc_d["coupling_map"], proc_d["num_qubits"]))})
    return pd.DataFrame(rows)


def to_qiskit_coupling_map(key: str):
    """Qiskit CouplingMap with both CX directions (needs qiskit; optional)."""
    from qiskit.transpiler import CouplingMap  # type: ignore
    proc = load_processor(key)
    both = [list(e) for e in proc["coupling_map"]] + [[b, a] for a, b in proc["coupling_map"]]
    return CouplingMap(both)


# ======================================================================================
# Building Processors A and B (Phase 1 qualification deliverable)
# ======================================================================================
FIXED_NOISE = {"type": "challenge_defined", "source": "Challenge Kit section 3.4",
               "single_qubit_depolarizing": 0.001, "cx_depolarizing": 0.005, "readout_bitflip": 0.01}
BENCHMARK = {"shots": 4096, "transpile_optimization_level": 1, "layout_routing": "SABRE", "seed": 42}


def build_processor_dict(key: str, variant: str = None) -> dict:
    """Processor definition built from participant's architectural exploration."""
    if key == "A":
        chosen = CANDIDATE_TOPOLOGIES["A"][variant or "reference_2016"]
        source = "2016-inspired 5-qubit reference architecture with synthetic noise model"
    else:
        chosen = CANDIDATE_TOPOLOGIES["B"][variant or "mesh_baseline"]
        source = "Processor B 9-qubit architecture specification"
    return {
        "name": chosen["name"],
        "source": source,
        "num_qubits": KIT_QUBITS[key],
        "topology": chosen["topology"],
        "coupling_map": [list(e) for e in chosen["coupling_map"]],
        "bidirectional": True,
        "basis_gates": ["rz", "sx", "x", "cx"],
        "noise": FIXED_NOISE,
        "benchmark": BENCHMARK,
        "note": chosen["description"],
    }


def write_processor_files() -> dict:
    """Generate only the required final-kit Processor A/B files and validate D."""
    out = {}
    (Path(PROCESSORS_DIR) / "processor_A.json").write_text(json.dumps(build_processor_dict("A"), indent=2) + "\n")
    out["A"] = validate("A") or "OK"
    (Path(PROCESSORS_DIR) / "processor_B.json").write_text(json.dumps(build_processor_dict("B"), indent=2) + "\n")
    out["B"] = validate("B") or "OK"
    if (Path(PROCESSORS_DIR) / "processor_D.json").exists():
        out["D"] = validate("D") or "OK"
    return out


# ---- routing-cost ESTIMATE in pure Python (no Qiskit needed) --------------------------------
def greedy_swap_count(g: nx.Graph, gates, layout=None) -> int:
    """SWAPs needed to execute a list of logical two-qubit gates on graph g, using a fixed initial
    layout (default: logical i -> physical i) and shortest-path SWAP insertion. This is an
    illustrative lower-effort estimate; the REQUIRED benchmark numbers come from Qiskit transpile
    (optimization_level=1, SABRE, seed 42) - see transpile_baseline()."""
    n = g.number_of_nodes()
    l2p = list(layout) if layout is not None else list(range(n))
    p2l = {p: l for l, p in enumerate(l2p)}
    swaps = 0
    for a, b in gates:
        pa, pb = l2p[a], l2p[b]
        if g.has_edge(pa, pb):
            continue
        path = nx.shortest_path(g, pa, pb)
        for x, y in zip(path[:-2], path[1:-1]):          # walk qubit a toward b until adjacent
            lx, ly = p2l[x], p2l[y]
            p2l[x], p2l[y] = ly, lx
            l2p[lx], l2p[ly] = y, x
            swaps += 1
    return swaps


ILLUSTRATIVE_WORKLOADS = {
    "GHZ-5 (chain CX)": [(0, 1), (1, 2), (2, 3), (3, 4)],
    "GHZ-5 (star CX from q0)": [(0, 1), (0, 2), (0, 3), (0, 4)],
    "Toffoli decomposition (q0,q1->q2)": [(1, 2), (0, 2), (1, 2), (0, 2), (0, 1)],
    "All-to-all 5 qubits (QFT-like)": [(a, b) for a in range(5) for b in range(a + 1, 5)],
}


def routing_estimate_table() -> pd.DataFrame:
    rows = []
    for key in ("A", "B"):
        proc = load_processor(key)
        g = build_graph(proc["coupling_map"], proc["num_qubits"])
        for name, gates in ILLUSTRATIVE_WORKLOADS.items():
            sw = greedy_swap_count(g, gates)
            rows.append({"workload": name, "processor": f"Processor {key}", "logical_2q_gates": len(gates),
                         "swaps_estimate": sw, "cx_estimate": len(gates) + 3 * sw,
                         "method": f"identity layout, {proc.get('topology', 'custom')}"})
    # Comparative candidate analysis as requested by organizers
    proc_d = load_processor("D")
    topos_to_compare = [
        ("A - 2016 Reference (Required)", CANDIDATE_TOPOLOGIES["A"]["reference_2016"]["coupling_map"], 5),
        ("A - Chain (optional candidate)", CANDIDATE_TOPOLOGIES["A"]["chain_baseline"]["coupling_map"], 5),
        ("A - Ring (optional candidate)", CANDIDATE_TOPOLOGIES["A"]["ring"]["coupling_map"], 5),
        ("B - Mesh-Loop (Required)", CANDIDATE_TOPOLOGIES["B"]["mesh_baseline"]["coupling_map"], 9),
        ("B - Sparse Tree (optional candidate)", CANDIDATE_TOPOLOGIES["B"]["tree_sparse"]["coupling_map"], 9),
        ("B - 3x3 Grid (optional candidate)", CANDIDATE_TOPOLOGIES["B"]["grid_3x3"]["coupling_map"], 9),
        ("D - 3x3 Grid (team design)", proc_d["coupling_map"], proc_d["num_qubits"]),
    ]
    for topo_name, cm, nq in topos_to_compare:
        g = build_graph(cm, nq)
        for name, gates in ILLUSTRATIVE_WORKLOADS.items():
            sw = greedy_swap_count(g, gates)
            rows.append({"workload": name, "processor": topo_name, "logical_2q_gates": len(gates),
                         "swaps_estimate": sw, "cx_estimate": len(gates) + 3 * sw,
                         "method": "candidate comparison"})
    return pd.DataFrame(rows)


# ---- Qiskit benchmark path (REQUIRES qiskit + qiskit-aer; not executed in the authoring sandbox) --
def fixed_noise_model():
    """Kit noise model: 1-qubit depolarizing 0.001 per 1q gate, CX depolarizing 0.005, readout flip 0.01."""
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error  # type: ignore
    nm = NoiseModel(basis_gates=["rz", "sx", "x", "cx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(FIXED_NOISE["single_qubit_depolarizing"], 1), ["rz", "sx", "x"])
    nm.add_all_qubit_quantum_error(depolarizing_error(FIXED_NOISE["cx_depolarizing"], 2), ["cx"])
    p = FIXED_NOISE["readout_bitflip"]
    nm.add_all_qubit_readout_error(ReadoutError([[1 - p, p], [p, 1 - p]]))
    return nm


def transpile_baseline(circuit, key: str, routing_only: bool = False):
    """Required baseline: optimization_level=1, SABRE layout + routing, seed 42, basis {rz,sx,x,cx}.
    routing_only=True keeps `swap` in the basis so inserted SWAPs can be counted."""
    from qiskit import transpile  # type: ignore
    proc = load_processor(key)
    basis = list(proc["basis_gates"]) + (["swap"] if routing_only else [])
    return transpile(circuit, coupling_map=to_qiskit_coupling_map(key), basis_gates=basis,
                     optimization_level=1, layout_method="sabre", routing_method="sabre", seed_transpiler=42)


def circuit_resources(compiled, routed) -> dict:
    ops = compiled.count_ops()
    used = {compiled.find_bit(q).index for inst in compiled.data for q in inst.qubits}
    return {"depth": compiled.depth(), "cx_count": ops.get("cx", 0),
            "single_qubit_gates": sum(v for k, v in ops.items() if k in ("rz", "sx", "x")),
            "swap_count": routed.count_ops().get("swap", 0), "physical_qubits_used": len(used)}


def grover_circuit(marked: str = "101", iterations: int = 2):
    """Grover search over 2^n keys (n = len(marked)): the quantum speed-up behind 'AES-128 -> ~64-bit
    security', which is why the channel uses AES-256-GCM."""
    from qiskit import QuantumCircuit  # type: ignore
    n = len(marked)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    zeros = [i for i, bit in enumerate(reversed(marked)) if bit == "0"]   # qiskit is little-endian
    for _ in range(iterations):
        for q in zeros:
            qc.x(q)
        qc.h(n - 1); qc.mcx(list(range(n - 1)), n - 1); qc.h(n - 1)        # phase oracle
        for q in zeros:
            qc.x(q)
        qc.h(range(n)); qc.x(range(n))                                      # diffuser
        qc.h(n - 1); qc.mcx(list(range(n - 1)), n - 1); qc.h(n - 1)
        qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def run_ab_experiment(circuit, expected: str, shots: int = 4096) -> pd.DataFrame:
    """Same logical circuit on Processor A and B with the fixed noise model: resources + success rate."""
    from qiskit_aer import AerSimulator  # type: ignore
    rows = []
    for key in ("A", "B"):
        compiled, routed = transpile_baseline(circuit, key), transpile_baseline(circuit, key, routing_only=True)
        noisy = AerSimulator(noise_model=fixed_noise_model(), seed_simulator=42).run(compiled, shots=shots).result().get_counts()
        ideal = AerSimulator(seed_simulator=42).run(compiled, shots=shots).result().get_counts()
        rows.append({"processor": key, **circuit_resources(compiled, routed), "shots": shots,
                     "p_success_ideal": ideal.get(expected, 0) / shots, "p_success_noisy": noisy.get(expected, 0) / shots,
                     "noise_model": "kit fixed model", "transpile": "opt_level=1, SABRE, seed=42"})
    return pd.DataFrame(rows)


def ghz5_circuit():
    """Return the measured star-GHZ circuit for processor architecture probing."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(5, 5, name="STAR-GHZ-5")
    qc.h(0)
    for q in range(1, 5):
        qc.cx(0, q)
    qc.measure(range(5), range(5))
    return qc


def run_probe(shots: int = 4096, seed: int = 42) -> list[dict]:
    """Transpile and simulate the star-GHZ-5 circuit on A, B, and D."""
    from qiskit import transpile, __version__ as qiskit_version
    from qiskit_aer import AerSimulator, __version__ as aer_version
    import csv, math
    from .problem import RESULTS_FIGURES, RESULTS_TABLES

    logical = ghz5_circuit()
    noise_model = fixed_noise_model()
    rows = []
    circuit_text = ["Logical circuit (same input on A, B, D):", str(logical)]
    basis_gates = ["rz", "sx", "x", "cx"]
    
    for key in ("A", "B", "D"):
        processor = load_processor(key)
        cmap = to_qiskit_coupling_map(key)
        compiled = transpile(
            logical,
            coupling_map=cmap,
            basis_gates=basis_gates,
            optimization_level=1,
            layout_method="sabre",
            routing_method="sabre",
            seed_transpiler=seed,
        )
        routed = transpile(
            logical,
            coupling_map=cmap,
            basis_gates=basis_gates + ["swap"],
            optimization_level=1,
            layout_method="sabre",
            routing_method="sabre",
            seed_transpiler=seed,
        )
        ideal_counts = AerSimulator(seed_simulator=seed).run(compiled, shots=shots).result().get_counts()
        noisy_counts = AerSimulator(noise_model=noise_model, seed_simulator=seed).run(compiled, shots=shots).result().get_counts()
        
        clean_ideal = {k.replace(" ", ""): v for k, v in ideal_counts.items()}
        clean_noisy = {k.replace(" ", ""): v for k, v in noisy_counts.items()}
        p_ideal = (clean_ideal.get("00000", 0) + clean_ideal.get("11111", 0)) / shots
        p_noisy = (clean_noisy.get("00000", 0) + clean_noisy.get("11111", 0)) / shots
        active = {compiled.find_bit(q).index for inst in compiled.data for q in inst.qubits}
        
        rows.append({
            "processor": key,
            "processor_name": processor["name"],
            "logical_qubits": logical.num_qubits,
            "physical_qubits_available": processor["num_qubits"],
            "physical_qubits_used": len(active),
            "cx_count": int(compiled.count_ops().get("cx", 0)),
            "depth": int(compiled.depth()),
            "swap_count": int(routed.count_ops().get("swap", 0)),
            "shots": shots,
            "p_success_ideal": p_ideal,
            "p_success_noisy": p_noisy,
            "noisy_standard_error": math.sqrt(p_noisy * (1 - p_noisy) / shots),
            "seed_transpiler": seed,
            "seed_simulator": seed,
        })
        circuit_text.extend([f"\nProcessor {key} transpiled circuit:", str(compiled)])

    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    RESULTS_FIGURES.mkdir(parents=True, exist_ok=True)
    with (RESULTS_TABLES / "architecture_probe.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def run_t1_t2_sweep(
    t1_values_us: list[float] | None = None,
    time_1q_ns: float = 35.0,
    time_2q_ns: float = 250.0,
    shots: int = 4096,
    seed: int = 42,
) -> list[dict]:
    """Sweep thermal relaxation (T1) and dephasing (T2) times across Processors A, B, and D."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, ReadoutError, thermal_relaxation_error
    import csv, math
    from .problem import RESULTS_TABLES

    if t1_values_us is None:
        t1_values_us = [15.0, 30.0, 50.0, 80.0, 120.0, 200.0]

    logical = ghz5_circuit()
    basis_gates = ["rz", "sx", "x", "cx"]
    compiled_circuits = {}
    for key in ("A", "B", "D"):
        cmap = to_qiskit_coupling_map(key)
        compiled_circuits[key] = transpile(
            logical,
            coupling_map=cmap,
            basis_gates=basis_gates,
            optimization_level=1,
            layout_method="sabre",
            routing_method="sabre",
            seed_transpiler=seed,
        )

    rows = []
    p_readout = FIXED_NOISE["readout_bitflip"]
    readout_err = ReadoutError([[1 - p_readout, p_readout], [p_readout, 1 - p_readout]])

    for t1_us in t1_values_us:
        t1_ns = t1_us * 1e3
        t2_ns = min(2.0 * t1_ns, t1_ns * 1.4)
        nm = NoiseModel(basis_gates=basis_gates)
        e1 = thermal_relaxation_error(t1_ns, t2_ns, time_1q_ns)
        e2 = thermal_relaxation_error(t1_ns, t2_ns, time_2q_ns).expand(
            thermal_relaxation_error(t1_ns, t2_ns, time_2q_ns)
        )
        nm.add_all_qubit_quantum_error(e1, ["rz", "sx", "x"])
        nm.add_all_qubit_quantum_error(e2, ["cx"])
        nm.add_all_qubit_readout_error(readout_err)

        sim = AerSimulator(noise_model=nm, seed_simulator=seed)
        row = {
            "t1_us": t1_us,
            "t2_us": round(t2_ns / 1e3, 1),
            "gate_time_1q_ns": time_1q_ns,
            "gate_time_2q_ns": time_2q_ns,
        }
        for key in ("A", "B", "D"):
            counts = sim.run(compiled_circuits[key], shots=shots).result().get_counts()
            clean = {k.replace(" ", ""): v for k, v in counts.items()}
            fid = (clean.get("00000", 0) + clean.get("11111", 0)) / shots
            row[f"fidelity_{key}"] = round(fid, 4)
            row[f"stderr_{key}"] = round(math.sqrt(fid * (1 - fid) / shots), 4)
        rows.append(row)

    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    with (RESULTS_TABLES / "t1_t2_sweep.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "build":
    print(write_processor_files())
